"""
Tests for Crystal and related types.

Tests the core crystallization concepts:
- MoodVector affective signatures
- Crystal creation and serialization
- CrystalLevel hierarchy

The Crystal model compresses semantic content (insight, significance) with
provenance (source_marks), unlike the old ExperienceCrystal which stored
raw thoughts. See spec/protocols/witness-crystallization.md.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.witness.crystal import (
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from services.witness.mark import MarkId

# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_mark_ids() -> list[MarkId]:
    """Create sample mark IDs for testing."""
    return [
        MarkId("mark-001"),
        MarkId("mark-002"),
        MarkId("mark-003"),
        MarkId("mark-004"),
    ]


@pytest.fixture
def sample_time_range() -> tuple[datetime, datetime]:
    """Create sample time range."""
    base_time = datetime.now()
    return (base_time, base_time + timedelta(minutes=30))


# =============================================================================
# MoodVector Tests
# =============================================================================


class TestMoodVector:
    """Tests for MoodVector affective signature."""

    def test_neutral_mood(self) -> None:
        """Neutral mood has all dimensions at 0.5."""
        mood = MoodVector.neutral()
        assert mood.warmth == 0.5
        assert mood.weight == 0.5
        assert mood.tempo == 0.5
        assert mood.texture == 0.5
        assert mood.brightness == 0.5
        assert mood.saturation == 0.5
        assert mood.complexity == 0.5

    def test_mood_from_empty_marks(self) -> None:
        """Empty marks produce neutral mood."""
        mood = MoodVector.from_marks([])
        assert mood == MoodVector.neutral()

    def test_mood_dimension_bounds(self) -> None:
        """All dimensions are clamped to [0, 1]."""
        # Create mood with out-of-bounds values
        mood = MoodVector(
            warmth=-0.5,
            weight=1.5,
            tempo=0.5,
            texture=0.5,
            brightness=0.5,
            saturation=0.5,
            complexity=0.5,
        )

        # Should be clamped
        assert mood.warmth >= 0.0
        assert mood.weight <= 1.0

    def test_mood_similarity_identical(self) -> None:
        """Identical moods have similarity 1.0."""
        mood = MoodVector(
            warmth=0.8,
            weight=0.3,
            tempo=0.6,
            texture=0.2,
            brightness=0.9,
            saturation=0.5,
            complexity=0.4,
        )
        assert mood.similarity(mood) == pytest.approx(1.0, abs=0.001)

    def test_mood_similarity_different(self) -> None:
        """Different moods have lower similarity."""
        mood1 = MoodVector(
            warmth=0.9,
            weight=0.1,
            tempo=0.9,
            texture=0.1,
            brightness=0.9,
            saturation=0.9,
            complexity=0.1,
        )
        mood2 = MoodVector(
            warmth=0.1,
            weight=0.9,
            tempo=0.1,
            texture=0.9,
            brightness=0.1,
            saturation=0.1,
            complexity=0.9,
        )

        similarity = mood1.similarity(mood2)
        assert similarity < 1.0
        assert similarity > -1.0  # Still positive due to all positive values

    def test_mood_to_dict_roundtrip(self) -> None:
        """Mood can be serialized and deserialized."""
        original = MoodVector(
            warmth=0.7,
            weight=0.3,
            tempo=0.8,
            texture=0.2,
            brightness=0.9,
            saturation=0.4,
            complexity=0.6,
        )
        data = original.to_dict()
        restored = MoodVector.from_dict(data)

        assert restored.warmth == original.warmth
        assert restored.brightness == original.brightness

    def test_dominant_quality(self) -> None:
        """Dominant quality is furthest from neutral."""
        mood = MoodVector(
            warmth=0.5,  # neutral
            weight=0.5,  # neutral
            tempo=0.5,  # neutral
            texture=0.5,  # neutral
            brightness=0.95,  # very bright - furthest from 0.5
            saturation=0.5,  # neutral
            complexity=0.5,  # neutral
        )
        assert mood.dominant_quality == "brightness"


# =============================================================================
# CrystalLevel Tests
# =============================================================================


class TestCrystalLevel:
    """Tests for CrystalLevel hierarchy."""

    def test_level_ordering(self) -> None:
        """Levels are ordered SESSION < DAY < WEEK < EPOCH."""
        assert CrystalLevel.SESSION < CrystalLevel.DAY
        assert CrystalLevel.DAY < CrystalLevel.WEEK
        assert CrystalLevel.WEEK < CrystalLevel.EPOCH

    def test_level_values(self) -> None:
        """Levels have expected integer values."""
        assert CrystalLevel.SESSION.value == 0
        assert CrystalLevel.DAY.value == 1
        assert CrystalLevel.WEEK.value == 2
        assert CrystalLevel.EPOCH.value == 3

    def test_level_display_name(self) -> None:
        """Levels have human-friendly display names."""
        assert CrystalLevel.SESSION.name_display == "Session"
        assert CrystalLevel.EPOCH.name_display == "Epoch"


# =============================================================================
# Crystal ID Tests
# =============================================================================


class TestCrystalId:
    """Tests for Crystal ID generation."""

    def test_generate_crystal_id_format(self) -> None:
        """Generated IDs have expected format."""
        crystal_id = generate_crystal_id()
        assert crystal_id.startswith("crystal-")
        assert len(crystal_id) == len("crystal-") + 12  # 12 hex chars

    def test_generate_crystal_id_uniqueness(self) -> None:
        """Each generated ID is unique."""
        ids = {generate_crystal_id() for _ in range(100)}
        assert len(ids) == 100


# =============================================================================
# Crystal Tests
# =============================================================================


class TestCrystal:
    """Tests for Crystal atomic memory unit."""

    def test_crystal_from_crystallization_basic(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """Create basic session crystal from crystallization."""
        crystal = Crystal.from_crystallization(
            insight="Completed routing refactor",
            significance="Cleaner architecture enables future work",
            principles=["composable", "tasteful"],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
            session_id="refactor-session",
        )

        assert crystal.level == CrystalLevel.SESSION
        assert crystal.insight == "Completed routing refactor"
        assert crystal.significance == "Cleaner architecture enables future work"
        assert "composable" in crystal.principles
        assert len(crystal.source_marks) == 4
        assert crystal.session_id == "refactor-session"
        assert crystal.time_range is not None

    def test_crystal_from_crystallization_with_options(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """Create crystal with all optional parameters."""
        mood = MoodVector(brightness=0.8, warmth=0.7)
        topics = {"refactoring", "routing", "tests"}

        crystal = Crystal.from_crystallization(
            insight="Major refactor complete",
            significance="Code is cleaner",
            principles=["composable"],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
            confidence=0.9,
            topics=topics,
            mood=mood,
            session_id="test",
        )

        assert crystal.confidence == 0.9
        assert crystal.topics == frozenset(topics)
        assert crystal.mood.brightness == 0.8
        assert crystal.mood.warmth == 0.7

    def test_crystal_level_0_requires_source_marks(self) -> None:
        """SESSION crystals use source_marks, not source_crystals."""
        # This should work - SESSION with source_marks
        crystal = Crystal.from_crystallization(
            insight="Test",
            significance="",
            principles=[],
            source_marks=[MarkId("mark-1")],
            time_range=(datetime.now(), datetime.now()),
        )
        assert crystal.level == CrystalLevel.SESSION

    def test_crystal_from_crystals_higher_level(self) -> None:
        """Create higher-level crystal from source crystals."""
        source_crystals = [
            generate_crystal_id(),
            generate_crystal_id(),
            generate_crystal_id(),
        ]

        crystal = Crystal.from_crystals(
            insight="Week summary",
            significance="Good progress made",
            principles=["joy-inducing"],
            source_crystals=source_crystals,
            level=CrystalLevel.WEEK,
        )

        assert crystal.level == CrystalLevel.WEEK
        assert len(crystal.source_crystals) == 3
        assert len(crystal.source_marks) == 0

    def test_crystal_from_crystals_rejects_session_level(self) -> None:
        """from_crystals raises for SESSION level."""
        with pytest.raises(ValueError, match="Use from_crystallization"):
            Crystal.from_crystals(
                insight="Test",
                significance="",
                principles=[],
                source_crystals=[generate_crystal_id()],
                level=CrystalLevel.SESSION,
            )

    def test_crystal_to_dict_roundtrip(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """Crystal can be serialized and deserialized."""
        original = Crystal.from_crystallization(
            insight="Test insight",
            significance="Test significance",
            principles=["composable", "tasteful"],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
            topics={"routing", "tests"},
            mood=MoodVector(brightness=0.8),
            session_id="test-session",
        )

        data = original.to_dict()
        restored = Crystal.from_dict(data)

        assert str(restored.id) == str(original.id)
        assert restored.level == original.level
        assert restored.insight == original.insight
        assert restored.significance == original.significance
        assert restored.principles == original.principles
        assert len(restored.source_marks) == len(original.source_marks)
        assert restored.session_id == original.session_id
        assert restored.mood.brightness == pytest.approx(original.mood.brightness, abs=0.01)

    def test_crystal_id_uniqueness(self) -> None:
        """Each crystal gets a unique ID."""
        now = datetime.now()
        crystal1 = Crystal.from_crystallization(
            insight="Test 1",
            significance="",
            principles=[],
            source_marks=[],
            time_range=(now, now),
        )
        crystal2 = Crystal.from_crystallization(
            insight="Test 2",
            significance="",
            principles=[],
            source_marks=[],
            time_range=(now, now),
        )

        assert crystal1.id != crystal2.id

    def test_crystal_source_count(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """source_count returns correct count."""
        crystal = Crystal.from_crystallization(
            insight="Test",
            significance="",
            principles=[],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
        )
        assert crystal.source_count == 4

    def test_crystal_duration_minutes(
        self,
        sample_mark_ids: list[MarkId],
    ) -> None:
        """duration_minutes computed from time_range."""
        start = datetime.now()
        end = start + timedelta(minutes=45)

        crystal = Crystal.from_crystallization(
            insight="Test",
            significance="",
            principles=[],
            source_marks=sample_mark_ids,
            time_range=(start, end),
        )
        assert crystal.duration_minutes == pytest.approx(45.0, abs=0.1)

    def test_crystal_duration_minutes_none_without_time_range(self) -> None:
        """duration_minutes is None without time_range."""
        crystal = Crystal(
            level=CrystalLevel.DAY,
            insight="Test",
            source_crystals=(generate_crystal_id(),),
        )
        assert crystal.duration_minutes is None

    def test_crystal_repr(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """Crystal has informative repr."""
        crystal = Crystal.from_crystallization(
            insight="Test",
            significance="",
            principles=[],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
        )
        repr_str = repr(crystal)

        assert "Crystal" in repr_str
        assert "SESSION" in repr_str
        assert "sources=4" in repr_str


# =============================================================================
# Crystal Law Tests
# =============================================================================


class TestCrystalLaws:
    """Tests for Crystal invariant laws."""

    def test_law_3_session_uses_marks(self) -> None:
        """Law 3: SESSION crystals use source_marks, not source_crystals."""
        now = datetime.now()
        # Valid: SESSION with marks
        crystal = Crystal.from_crystallization(
            insight="Test",
            significance="",
            principles=[],
            source_marks=[MarkId("m1")],
            time_range=(now, now),
        )
        assert crystal.level == CrystalLevel.SESSION
        assert len(crystal.source_marks) > 0

    def test_law_3_higher_levels_use_crystals(self) -> None:
        """Law 3: Higher-level crystals use source_crystals."""
        crystal = Crystal.from_crystals(
            insight="Week summary",
            significance="",
            principles=[],
            source_crystals=[generate_crystal_id()],
            level=CrystalLevel.WEEK,
        )
        assert crystal.level == CrystalLevel.WEEK
        assert len(crystal.source_crystals) > 0
        assert len(crystal.source_marks) == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestCrystalIntegration:
    """Integration tests for the Crystal model."""

    def test_full_crystallization_pipeline(
        self,
        sample_mark_ids: list[MarkId],
        sample_time_range: tuple[datetime, datetime],
    ) -> None:
        """Test complete crystallization from marks to serialization."""
        # Create crystal
        crystal = Crystal.from_crystallization(
            insight="Completed refactoring of routing module",
            significance="Better separation of concerns",
            principles=["composable", "tasteful"],
            source_marks=sample_mark_ids,
            time_range=sample_time_range,
            topics={"routing", "refactoring"},
            mood=MoodVector(brightness=0.8, warmth=0.7),
            session_id="integration-test",
        )

        # Verify all components
        assert crystal.source_count > 0
        assert crystal.mood != MoodVector.neutral()
        assert crystal.insight != ""
        assert len(crystal.topics) > 0

        # Serialize and deserialize
        data = crystal.to_dict()
        restored = Crystal.from_dict(data)
        assert restored.session_id == crystal.session_id
        assert restored.source_count == crystal.source_count

    def test_mood_affects_retrieval(self) -> None:
        """Similar moods should have high similarity for retrieval."""
        bright_mood = MoodVector(brightness=0.9, warmth=0.8)
        also_bright_mood = MoodVector(brightness=0.85, warmth=0.75)
        dark_mood = MoodVector(brightness=0.2, warmth=0.3)

        # Similar moods should have high similarity
        assert bright_mood.similarity(also_bright_mood) > 0.9

        # Different moods should have lower similarity
        assert bright_mood.similarity(dark_mood) < bright_mood.similarity(also_bright_mood)


# =============================================================================
# Property-Based Tests (Optional - requires hypothesis)
# =============================================================================


try:
    from hypothesis import given, settings, strategies as st

    class TestMoodVectorProperties:
        """Property-based tests for MoodVector."""

        @given(
            warmth=st.floats(min_value=0.0, max_value=1.0),
            weight=st.floats(min_value=0.0, max_value=1.0),
            tempo=st.floats(min_value=0.0, max_value=1.0),
            texture=st.floats(min_value=0.0, max_value=1.0),
            brightness=st.floats(min_value=0.0, max_value=1.0),
            saturation=st.floats(min_value=0.0, max_value=1.0),
            complexity=st.floats(min_value=0.0, max_value=1.0),
        )
        @settings(max_examples=50)
        def test_mood_self_similarity_is_one(
            self,
            warmth: float,
            weight: float,
            tempo: float,
            texture: float,
            brightness: float,
            saturation: float,
            complexity: float,
        ) -> None:
            """Any mood has similarity 1.0 with itself."""
            mood = MoodVector(
                warmth=warmth,
                weight=weight,
                tempo=tempo,
                texture=texture,
                brightness=brightness,
                saturation=saturation,
                complexity=complexity,
            )
            assert mood.similarity(mood) == pytest.approx(1.0, abs=0.001)

        @given(
            warmth=st.floats(min_value=0.0, max_value=1.0),
            weight=st.floats(min_value=0.0, max_value=1.0),
        )
        @settings(max_examples=20)
        def test_mood_serialization_roundtrip(self, warmth: float, weight: float) -> None:
            """Mood survives serialization roundtrip."""
            original = MoodVector(warmth=warmth, weight=weight)
            restored = MoodVector.from_dict(original.to_dict())
            assert restored.warmth == pytest.approx(original.warmth, abs=0.001)
            assert restored.weight == pytest.approx(original.weight, abs=0.001)

except ImportError:
    pass  # hypothesis not installed, skip property tests
