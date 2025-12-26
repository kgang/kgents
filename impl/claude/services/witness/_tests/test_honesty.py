"""
Tests for Crystal Honesty Module (Amendment G Compliance).

Tests verify:
1. CompressionHonesty dataclass behavior
2. CrystalHonestyCalculator computes correct metrics
3. Warm disclosure messages follow WARMTH principle
4. Galois loss computed correctly (with fallback)
5. Factory functions work properly

WARMTH Principle Verification:
- No shaming language ("You missed...", "You failed...")
- Acknowledgment tone ("Some moments were compressed...")
- Kind companion voice
"""

from datetime import datetime

import pytest

from services.witness.crystal import Crystal, CrystalLevel, generate_crystal_id
from services.witness.honesty import (
    DISCLOSURE_TEMPLATES,
    TAG_FRIENDLY_NAMES,
    CompressionHonesty,
    CrystalHonestyCalculator,
    get_honesty_calculator,
    reset_honesty_calculator,
)
from services.witness.mark import (
    Mark,
    MarkId,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_marks() -> list[Mark]:
    """Create sample marks for testing."""
    marks = []
    for i in range(10):
        mark = Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            domain="journal",
            stimulus=Stimulus(
                kind="daily_note",
                content=f"Test note {i}",
                source="daily_lab",
            ),
            response=Response(
                kind="thought",
                content=f"This is test content for mark {i}. It has some substance.",
                success=True,
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=datetime.now(),
            tags=("eureka",) if i % 3 == 0 else ("friction",) if i % 2 == 0 else (),
        )
        marks.append(mark)
    return marks


@pytest.fixture
def sample_crystal(sample_marks: list[Mark]) -> Crystal:
    """Create a sample crystal from marks."""
    kept_marks = sample_marks[:5]  # Keep first 5 of 10
    return Crystal.from_crystallization(
        insight="Key insights from the day's work.",
        significance="Progress was made on important tasks.",
        principles=["tasteful", "composable"],
        source_marks=[MarkId(str(m.id)) for m in kept_marks],
        time_range=(datetime.now(), datetime.now()),
        confidence=0.8,
    )


@pytest.fixture
def calculator() -> CrystalHonestyCalculator:
    """Create a fresh calculator (no semantic distance for fast tests)."""
    return CrystalHonestyCalculator(
        use_semantic_distance=False,
        fallback_to_heuristic=True,
    )


# =============================================================================
# CompressionHonesty Tests
# =============================================================================


class TestCompressionHonesty:
    """Tests for the CompressionHonesty dataclass."""

    def test_creation(self):
        """Test basic creation."""
        honesty = CompressionHonesty(
            galois_loss=0.25,
            dropped_tags=["breakthroughs", "delights"],
            dropped_summaries=["First thing...", "Second thing..."],
            preserved_ratio=0.6,
            warm_disclosure="Your day condensed nicely.",
        )

        assert honesty.galois_loss == 0.25
        assert honesty.dropped_tags == ["breakthroughs", "delights"]
        assert honesty.preserved_ratio == 0.6
        assert "condensed" in honesty.warm_disclosure

    def test_quality_tier_excellent(self):
        """Test excellent tier (L < 0.1)."""
        honesty = CompressionHonesty(
            galois_loss=0.05,
            dropped_tags=[],
            dropped_summaries=[],
            preserved_ratio=0.95,
            warm_disclosure="test",
        )
        assert honesty.quality_tier == "excellent"

    def test_quality_tier_good(self):
        """Test good tier (0.1 <= L < 0.3)."""
        honesty = CompressionHonesty(
            galois_loss=0.2,
            dropped_tags=[],
            dropped_summaries=[],
            preserved_ratio=0.8,
            warm_disclosure="test",
        )
        assert honesty.quality_tier == "good"

    def test_quality_tier_moderate(self):
        """Test moderate tier (0.3 <= L < 0.5)."""
        honesty = CompressionHonesty(
            galois_loss=0.4,
            dropped_tags=[],
            dropped_summaries=[],
            preserved_ratio=0.6,
            warm_disclosure="test",
        )
        assert honesty.quality_tier == "moderate"

    def test_quality_tier_significant(self):
        """Test significant tier (L >= 0.5)."""
        honesty = CompressionHonesty(
            galois_loss=0.7,
            dropped_tags=[],
            dropped_summaries=[],
            preserved_ratio=0.3,
            warm_disclosure="test",
        )
        assert honesty.quality_tier == "significant"

    def test_to_dict_and_from_dict(self):
        """Test serialization roundtrip."""
        original = CompressionHonesty(
            galois_loss=0.25,
            dropped_tags=["learning moments"],
            dropped_summaries=["Test summary..."],
            preserved_ratio=0.75,
            warm_disclosure="Kept the heart of your work.",
        )

        data = original.to_dict()
        restored = CompressionHonesty.from_dict(data)

        assert restored.galois_loss == original.galois_loss
        assert restored.dropped_tags == original.dropped_tags
        assert restored.dropped_summaries == original.dropped_summaries
        assert restored.preserved_ratio == original.preserved_ratio
        assert restored.warm_disclosure == original.warm_disclosure

    def test_repr(self):
        """Test string representation."""
        honesty = CompressionHonesty(
            galois_loss=0.25,
            dropped_tags=[],
            dropped_summaries=[],
            preserved_ratio=0.75,
            warm_disclosure="test",
        )
        repr_str = repr(honesty)
        assert "0.25" in repr_str
        assert "75%" in repr_str
        assert "good" in repr_str


# =============================================================================
# CrystalHonestyCalculator Tests
# =============================================================================


class TestCrystalHonestyCalculator:
    """Tests for the CrystalHonestyCalculator class."""

    @pytest.mark.asyncio
    async def test_compute_honesty_basic(
        self,
        calculator: CrystalHonestyCalculator,
        sample_marks: list[Mark],
        sample_crystal: Crystal,
    ):
        """Test basic honesty computation."""
        kept_marks = sample_marks[:5]
        honesty = await calculator.compute_honesty(
            original_marks=sample_marks,
            crystal=sample_crystal,
            kept_marks=kept_marks,
        )

        # 5 of 10 kept = 50% preserved
        assert honesty.preserved_ratio == 0.5
        assert len(honesty.dropped_summaries) <= 3  # Max 3 summaries
        assert honesty.warm_disclosure  # Non-empty disclosure

    @pytest.mark.asyncio
    async def test_compute_honesty_empty_marks(
        self,
        calculator: CrystalHonestyCalculator,
        sample_crystal: Crystal,
    ):
        """Test honesty computation with empty marks."""
        honesty = await calculator.compute_honesty(
            original_marks=[],
            crystal=sample_crystal,
        )

        assert honesty.galois_loss == 0.0
        assert honesty.preserved_ratio == 1.0
        assert "quiet" in honesty.warm_disclosure.lower()

    @pytest.mark.asyncio
    async def test_compute_honesty_all_preserved(
        self,
        calculator: CrystalHonestyCalculator,
        sample_marks: list[Mark],
    ):
        """Test when all marks are preserved."""
        crystal = Crystal.from_crystallization(
            insight="All content preserved.",
            significance="Nothing dropped.",
            principles=["tasteful"],
            source_marks=[MarkId(str(m.id)) for m in sample_marks],
            time_range=(datetime.now(), datetime.now()),
            confidence=1.0,
        )

        honesty = await calculator.compute_honesty(
            original_marks=sample_marks,
            crystal=crystal,
            kept_marks=sample_marks,
        )

        assert honesty.preserved_ratio == 1.0
        assert honesty.galois_loss < 0.1  # Heuristic: no content dropped
        assert len(honesty.dropped_tags) == 0

    @pytest.mark.asyncio
    async def test_dropped_tags_use_friendly_names(
        self,
        calculator: CrystalHonestyCalculator,
        sample_marks: list[Mark],
        sample_crystal: Crystal,
    ):
        """Test that dropped tags use friendly names."""
        # Marks have 'eureka' and 'friction' tags
        kept_marks = sample_marks[:3]  # Keep few, drop some with tags
        honesty = await calculator.compute_honesty(
            original_marks=sample_marks,
            crystal=sample_crystal,
            kept_marks=kept_marks,
        )

        # Should use friendly names like "breakthroughs", "resistance points"
        for tag in honesty.dropped_tags:
            # Either a friendly name or the raw tag
            assert tag in TAG_FRIENDLY_NAMES.values() or tag in TAG_FRIENDLY_NAMES.keys()

    def test_heuristic_loss_calculation(
        self,
        calculator: CrystalHonestyCalculator,
        sample_marks: list[Mark],
    ):
        """Test the heuristic loss fallback."""
        kept_marks = sample_marks[:5]

        loss = calculator._heuristic_loss(sample_marks, kept_marks)

        # 5 of 10 marks kept, roughly 50% content dropped
        assert 0.4 <= loss <= 0.6

    def test_heuristic_loss_empty(self, calculator: CrystalHonestyCalculator):
        """Test heuristic with empty input."""
        loss = calculator._heuristic_loss([], [])
        assert loss == 0.0


# =============================================================================
# WARMTH Principle Tests
# =============================================================================


class TestWarmthPrinciple:
    """Tests verifying WARMTH principle in disclosure messages."""

    # Forbidden patterns (shaming language)
    FORBIDDEN_PATTERNS = [
        "you missed",
        "you failed",
        "error in",
        "mistake",
        "wrong",
        "bad",
        "poor",
        "inadequate",
    ]

    def test_disclosure_templates_follow_warmth(self):
        """Verify all templates avoid shaming language."""
        for tier, templates in DISCLOSURE_TEMPLATES.items():
            for template in templates:
                template_lower = template.lower()
                for forbidden in self.FORBIDDEN_PATTERNS:
                    assert forbidden not in template_lower, (
                        f"Template '{template}' in tier '{tier}' "
                        f"contains forbidden pattern '{forbidden}'"
                    )

    def test_generate_warm_disclosure_no_shaming(self):
        """Test generated disclosures avoid shaming."""
        calculator = CrystalHonestyCalculator()

        # Test across all loss levels
        for loss in [0.05, 0.2, 0.4, 0.7]:
            disclosure = calculator.generate_warm_disclosure(
                galois_loss=loss,
                dropped_tags=["learning moments", "resistance points"],
                dropped_count=5,
                total_count=10,
            )

            disclosure_lower = disclosure.lower()
            for forbidden in self.FORBIDDEN_PATTERNS:
                assert forbidden not in disclosure_lower, (
                    f"Disclosure '{disclosure}' contains "
                    f"forbidden pattern '{forbidden}'"
                )

    def test_excellent_tier_uses_positive_language(self):
        """Test excellent tier has positive, affirming language."""
        calculator = CrystalHonestyCalculator()

        disclosure = calculator.generate_warm_disclosure(
            galois_loss=0.05,
            dropped_tags=[],
            dropped_count=1,
            total_count=10,
        )

        # Should contain positive words
        positive_words = ["beautifully", "preserved", "full", "light", "everything"]
        has_positive = any(word in disclosure.lower() for word in positive_words)
        assert has_positive, f"Excellent tier disclosure lacks positive language: {disclosure}"

    def test_significant_tier_still_warm(self):
        """Test even significant compression uses warm language."""
        calculator = CrystalHonestyCalculator()

        disclosure = calculator.generate_warm_disclosure(
            galois_loss=0.7,
            dropped_tags=["friction"],
            dropped_count=15,
            total_count=20,
        )

        # Should acknowledge but not shame
        assert "lost" not in disclosure.lower() or "nothing is lost" in disclosure.lower()
        assert any(
            phrase in disclosure.lower()
            for phrase in ["remain", "always", "core", "distilled", "resting"]
        ), f"Significant tier lacks reassurance: {disclosure}"


# =============================================================================
# Quality Description Tests
# =============================================================================


class TestQualityDescription:
    """Tests for quality description helper."""

    def test_excellent_description(self):
        """Test excellent quality description."""
        desc = CrystalHonestyCalculator.quality_description(0.05)
        assert "excellent" in desc.lower()

    def test_good_description(self):
        """Test good quality description."""
        desc = CrystalHonestyCalculator.quality_description(0.2)
        assert "good" in desc.lower()

    def test_moderate_description(self):
        """Test moderate quality description."""
        desc = CrystalHonestyCalculator.quality_description(0.4)
        assert "moderate" in desc.lower()

    def test_significant_description(self):
        """Test significant quality description."""
        desc = CrystalHonestyCalculator.quality_description(0.7)
        assert "significant" in desc.lower()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for singleton factory functions."""

    def test_get_honesty_calculator_singleton(self):
        """Test singleton behavior."""
        reset_honesty_calculator()

        calc1 = get_honesty_calculator()
        calc2 = get_honesty_calculator()

        assert calc1 is calc2

    def test_reset_honesty_calculator(self):
        """Test reset clears singleton."""
        calc1 = get_honesty_calculator()
        reset_honesty_calculator()
        calc2 = get_honesty_calculator()

        assert calc1 is not calc2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_single_mark_preserved(self):
        """Test with single mark fully preserved."""
        calculator = CrystalHonestyCalculator(use_semantic_distance=False)

        mark = Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            domain="journal",
            stimulus=Stimulus(kind="daily_note", content="Single note", source="test"),
            response=Response(kind="thought", content="Single content", success=True),
            umwelt=UmweltSnapshot.witness(),
            timestamp=datetime.now(),
        )

        crystal = Crystal.from_crystallization(
            insight="Single insight",
            significance="Single significance",
            principles=["tasteful"],
            source_marks=[MarkId(str(mark.id))],
            time_range=(datetime.now(), datetime.now()),
            confidence=1.0,
        )

        honesty = await calculator.compute_honesty(
            original_marks=[mark],
            crystal=crystal,
            kept_marks=[mark],
        )

        assert honesty.preserved_ratio == 1.0
        assert len(honesty.dropped_tags) == 0
        assert len(honesty.dropped_summaries) == 0

    @pytest.mark.asyncio
    async def test_all_marks_dropped_except_minimum(self):
        """Test with nearly all marks dropped."""
        calculator = CrystalHonestyCalculator(use_semantic_distance=False)

        marks = []
        for i in range(20):
            marks.append(Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                domain="journal",
                stimulus=Stimulus(kind="daily_note", content=f"Note {i}", source="test"),
                response=Response(kind="thought", content=f"Content {i} with substance", success=True),
                umwelt=UmweltSnapshot.witness(),
                timestamp=datetime.now(),
                tags=("eureka",) if i == 0 else ("friction",),
            ))

        # Keep only 1 of 20
        kept_marks = marks[:1]

        crystal = Crystal.from_crystallization(
            insight="Minimal crystal",
            significance="Heavy compression",
            principles=["curated"],
            source_marks=[MarkId(str(m.id)) for m in kept_marks],
            time_range=(datetime.now(), datetime.now()),
            confidence=0.5,
        )

        honesty = await calculator.compute_honesty(
            original_marks=marks,
            crystal=crystal,
            kept_marks=kept_marks,
        )

        assert honesty.preserved_ratio == 0.05  # 1 of 20
        assert honesty.quality_tier == "significant"  # High loss
        assert "resistance points" in honesty.dropped_tags or "friction" in honesty.dropped_tags

    def test_galois_loss_boundary_values(self):
        """Test boundary values for Galois loss tiers."""
        calc = CrystalHonestyCalculator()

        # Test exact boundaries
        assert calc.quality_description(0.0) == "excellent preservation"
        assert calc.quality_description(0.1) == "good compression"
        assert calc.quality_description(0.3) == "moderate compression"
        assert calc.quality_description(0.5) == "significant compression"
        assert calc.quality_description(1.0) == "significant compression"

    @pytest.mark.asyncio
    async def test_marks_without_tags(self):
        """Test marks without tags don't break tag processing."""
        calculator = CrystalHonestyCalculator(use_semantic_distance=False)

        marks = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                domain="journal",
                stimulus=Stimulus(kind="note", content="Test", source="test"),
                response=Response(kind="thought", content="No tags here", success=True),
                umwelt=UmweltSnapshot.witness(),
                timestamp=datetime.now(),
                tags=(),  # Empty tags
            )
            for _ in range(5)
        ]

        crystal = Crystal.from_crystallization(
            insight="Test crystal",
            significance="Test",
            principles=[],
            source_marks=[MarkId(str(marks[0].id))],
            time_range=(datetime.now(), datetime.now()),
            confidence=0.8,
        )

        honesty = await calculator.compute_honesty(
            original_marks=marks,
            crystal=crystal,
            kept_marks=[marks[0]],
        )

        # Should work without errors
        assert honesty.dropped_tags == []
