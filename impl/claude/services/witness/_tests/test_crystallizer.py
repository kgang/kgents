"""
Tests for the unified Crystal system.

Tests cover:
- Crystal model creation and validation
- CrystalStore append-only ledger
- Crystallizer LLM and template fallback
- Level consistency laws
- Provenance chain integrity

See: spec/protocols/witness-crystallization.md
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from services.witness.crystal import (
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from services.witness.crystal_store import (
    CrystalNotFoundError,
    CrystalQuery,
    CrystalStore,
    DuplicateCrystalError,
    LevelConsistencyError,
)
from services.witness.crystallizer import (
    CrystallizationResult,
    Crystallizer,
)
from services.witness.mark import (
    Mark,
    MarkId,
    NPhase,
    Response,
    Stimulus,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_marks() -> list[Mark]:
    """Create sample marks for testing."""
    now = datetime.now()
    return [
        Mark(
            id=MarkId(f"mark-{i}"),
            timestamp=now + timedelta(minutes=i),
            origin="test",
            stimulus=Stimulus(kind="action", content=f"Action {i}"),
            response=Response(kind="mark", content=f"Did thing {i}"),
            tags=("test", "composable") if i % 2 == 0 else ("test",),
            phase=NPhase.ACT,
            metadata={"reasoning": f"Because {i}"},  # Store reasoning in metadata
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_crystal() -> Crystal:
    """Create a sample level-0 crystal."""
    now = datetime.now()
    return Crystal.from_crystallization(
        insight="Completed 10 test actions",
        significance="Validated the test suite works",
        principles=["composable", "tasteful"],
        source_marks=[MarkId(f"mark-{i}") for i in range(10)],
        time_range=(now, now + timedelta(hours=1)),
        confidence=0.85,
        topics={"testing", "validation"},
        session_id="test-session-1",
    )


@pytest.fixture
def crystal_store() -> CrystalStore:
    """Create a fresh crystal store for testing."""
    return CrystalStore()


# =============================================================================
# Crystal Model Tests
# =============================================================================


class TestCrystal:
    """Tests for the Crystal dataclass."""

    def test_crystal_creation_level_0(self, sample_marks: list[Mark]) -> None:
        """Test creating a level-0 crystal from marks."""
        now = datetime.now()
        crystal = Crystal.from_crystallization(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[m.id for m in sample_marks],
            time_range=(now, now + timedelta(hours=1)),
        )

        assert crystal.level == CrystalLevel.SESSION
        assert crystal.insight == "Test insight"
        assert len(crystal.source_marks) == 10
        assert len(crystal.source_crystals) == 0
        assert crystal.source_count == 10

    def test_crystal_immutable(self, sample_crystal: Crystal) -> None:
        """Test that crystals are frozen (immutable)."""
        with pytest.raises(AttributeError):
            sample_crystal.insight = "Modified"  # type: ignore

    def test_source_marks_only_for_level_0(self) -> None:
        """Test Law 3: Level 0 must use source_marks."""
        now = datetime.now()

        # Valid: Level 0 with source_marks
        crystal = Crystal(
            level=CrystalLevel.SESSION,
            insight="Test",
            source_marks=(MarkId("mark-1"),),
            time_range=(now, now),
        )
        assert crystal.level == CrystalLevel.SESSION

    def test_source_crystals_only_for_level_1_plus(self) -> None:
        """Test Law 3: Level 1+ must use source_crystals."""
        # Valid: Level 1 with source_crystals
        crystal = Crystal.from_crystals(
            insight="Day insight",
            significance="Day significance",
            principles=["composable"],
            source_crystals=[CrystalId("crystal-1")],
            level=CrystalLevel.DAY,
        )
        assert crystal.level == CrystalLevel.DAY

    def test_level_1_cannot_use_source_marks(self) -> None:
        """Test that level 1+ cannot use source_marks."""
        with pytest.raises(ValueError, match="must use source_crystals"):
            Crystal(
                level=CrystalLevel.DAY,
                insight="Invalid",
                source_marks=(MarkId("mark-1"),),
            )

    def test_time_range_contains_sources(self, sample_crystal: Crystal) -> None:
        """Test that time_range contains source times."""
        assert sample_crystal.time_range is not None
        start, end = sample_crystal.time_range
        assert start <= end

    def test_to_dict_roundtrip(self, sample_crystal: Crystal) -> None:
        """Test serialization/deserialization roundtrip."""
        data = sample_crystal.to_dict()
        restored = Crystal.from_dict(data)

        assert restored.id == sample_crystal.id
        assert restored.level == sample_crystal.level
        assert restored.insight == sample_crystal.insight
        assert restored.significance == sample_crystal.significance
        assert restored.principles == sample_crystal.principles
        assert restored.source_marks == sample_crystal.source_marks
        assert restored.confidence == sample_crystal.confidence

    def test_crystal_id_generation(self) -> None:
        """Test that crystal IDs are unique."""
        ids = [generate_crystal_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique


class TestCrystalLevel:
    """Tests for the CrystalLevel enum."""

    def test_level_ordering(self) -> None:
        """Test that levels are ordered correctly."""
        assert CrystalLevel.SESSION < CrystalLevel.DAY
        assert CrystalLevel.DAY < CrystalLevel.WEEK
        assert CrystalLevel.WEEK < CrystalLevel.EPOCH

    def test_level_values(self) -> None:
        """Test level integer values."""
        assert CrystalLevel.SESSION.value == 0
        assert CrystalLevel.DAY.value == 1
        assert CrystalLevel.WEEK.value == 2
        assert CrystalLevel.EPOCH.value == 3

    def test_level_display_names(self) -> None:
        """Test human-friendly display names."""
        assert CrystalLevel.SESSION.name_display == "Session"
        assert CrystalLevel.DAY.name_display == "Day"
        assert CrystalLevel.WEEK.name_display == "Week"
        assert CrystalLevel.EPOCH.name_display == "Epoch"


class TestMoodVector:
    """Tests for the MoodVector affective signature."""

    def test_neutral_mood(self) -> None:
        """Test neutral mood creation."""
        mood = MoodVector.neutral()
        assert mood.warmth == 0.5
        assert mood.brightness == 0.5
        assert mood.tempo == 0.5

    def test_mood_from_marks(self, sample_marks: list[Mark]) -> None:
        """Test deriving mood from marks."""
        mood = MoodVector.from_marks(sample_marks)

        # Should have non-neutral values from mark signals
        assert isinstance(mood.warmth, float)
        assert isinstance(mood.brightness, float)
        assert 0.0 <= mood.warmth <= 1.0
        assert 0.0 <= mood.brightness <= 1.0

    def test_mood_from_empty_marks(self) -> None:
        """Test mood from empty marks returns neutral."""
        mood = MoodVector.from_marks([])
        assert mood == MoodVector.neutral()

    def test_mood_similarity(self) -> None:
        """Test cosine similarity between moods."""
        mood1 = MoodVector(warmth=0.8, brightness=0.9, tempo=0.7)
        mood2 = MoodVector(warmth=0.7, brightness=0.85, tempo=0.65)
        mood3 = MoodVector(warmth=0.1, brightness=0.2, tempo=0.3)

        # Similar moods should have high similarity
        sim_similar = mood1.similarity(mood2)
        assert sim_similar > 0.9

        # Different moods should have lower similarity
        sim_different = mood1.similarity(mood3)
        assert sim_different < sim_similar

    def test_mood_clamping(self) -> None:
        """Test that mood values are clamped to [0, 1]."""
        mood = MoodVector(warmth=1.5, brightness=-0.5)
        assert mood.warmth == 1.0
        assert mood.brightness == 0.0

    def test_mood_to_dict(self) -> None:
        """Test mood serialization."""
        mood = MoodVector(warmth=0.7, weight=0.3)
        data = mood.to_dict()

        assert data["warmth"] == 0.7
        assert data["weight"] == 0.3

    def test_mood_dominant_quality(self) -> None:
        """Test finding dominant mood quality."""
        mood = MoodVector(warmth=0.9, brightness=0.5, tempo=0.5)
        assert mood.dominant_quality == "warmth"


# =============================================================================
# CrystalStore Tests
# =============================================================================


class TestCrystalStore:
    """Tests for the CrystalStore append-only ledger."""

    def test_append_crystal(
        self,
        crystal_store: CrystalStore,
        sample_crystal: Crystal,
    ) -> None:
        """Test appending a crystal to the store."""
        crystal_store.append(sample_crystal)

        retrieved = crystal_store.get(sample_crystal.id)
        assert retrieved == sample_crystal
        assert len(crystal_store) == 1

    def test_duplicate_crystal_error(
        self,
        crystal_store: CrystalStore,
        sample_crystal: Crystal,
    ) -> None:
        """Test that duplicate IDs raise error."""
        crystal_store.append(sample_crystal)

        with pytest.raises(DuplicateCrystalError):
            crystal_store.append(sample_crystal)

    def test_query_by_level(self, crystal_store: CrystalStore) -> None:
        """Test querying crystals by level."""
        now = datetime.now()

        # Add session crystals
        session_crystals = []
        for i in range(3):
            c = Crystal.from_crystallization(
                insight=f"Session {i}",
                significance="",
                principles=[],
                source_marks=[MarkId(f"mark-{i}")],
                time_range=(now, now),
            )
            crystal_store.append(c)
            session_crystals.append(c)

        # Add a day crystal (requires session crystals to exist)
        day_crystal = Crystal.from_crystals(
            insight="Day summary",
            significance="",
            principles=[],
            source_crystals=[c.id for c in session_crystals],
            level=CrystalLevel.DAY,
        )
        crystal_store.append(day_crystal)

        # Query by level
        sessions = crystal_store.by_level(CrystalLevel.SESSION)
        days = crystal_store.by_level(CrystalLevel.DAY)

        assert len(sessions) == 3
        assert len(days) == 1
        assert days[0].insight == "Day summary"

    def test_query_by_time_range(self, crystal_store: CrystalStore) -> None:
        """Test querying crystals by time range."""
        now = datetime.now()

        # Add crystals at different times
        old_crystal = Crystal.from_crystallization(
            insight="Old",
            significance="",
            principles=[],
            source_marks=[MarkId("mark-0")],
            time_range=(now - timedelta(days=7), now - timedelta(days=7)),
        )
        # Manually set crystallized_at
        old_data = old_crystal.to_dict()
        old_data["crystallized_at"] = (now - timedelta(days=7)).isoformat()
        old_crystal = Crystal.from_dict(old_data)

        new_crystal = Crystal.from_crystallization(
            insight="New",
            significance="",
            principles=[],
            source_marks=[MarkId("mark-1")],
            time_range=(now, now),
        )

        crystal_store.append(old_crystal)
        crystal_store.append(new_crystal)

        # Query recent only
        query = CrystalQuery(after=now - timedelta(days=1))
        results = list(crystal_store.query(query))

        assert len(results) == 1
        assert results[0].insight == "New"

    def test_expand_session_crystal(
        self,
        crystal_store: CrystalStore,
        sample_crystal: Crystal,
    ) -> None:
        """Test expanding a session crystal shows mark IDs."""
        crystal_store.append(sample_crystal)

        sources = crystal_store.expand(sample_crystal.id)

        assert len(sources) == 10
        # MarkId is a NewType(str), so check for string
        assert all(isinstance(s, str) and s.startswith("mark-") for s in sources)

    def test_expand_day_crystal(self, crystal_store: CrystalStore) -> None:
        """Test expanding a day crystal shows source crystals."""
        now = datetime.now()

        # Create session crystals
        session_crystals = []
        for i in range(3):
            c = Crystal.from_crystallization(
                insight=f"Session {i}",
                significance="",
                principles=[],
                source_marks=[MarkId(f"mark-{i}")],
                time_range=(now, now),
            )
            crystal_store.append(c)
            session_crystals.append(c)

        # Create day crystal
        day_crystal = Crystal.from_crystals(
            insight="Day",
            significance="",
            principles=[],
            source_crystals=[c.id for c in session_crystals],
            level=CrystalLevel.DAY,
        )
        crystal_store.append(day_crystal)

        # Expand day crystal
        sources = crystal_store.expand(day_crystal.id)

        assert len(sources) == 3
        assert all(isinstance(s, Crystal) for s in sources)

    def test_level_consistency_validation(self, crystal_store: CrystalStore) -> None:
        """Test that level consistency is validated on append."""
        now = datetime.now()

        # Create a session crystal
        session = Crystal.from_crystallization(
            insight="Session",
            significance="",
            principles=[],
            source_marks=[MarkId("mark-0")],
            time_range=(now, now),
        )
        crystal_store.append(session)

        # Try to create a WEEK crystal from SESSION (skipping DAY)
        # This should fail because week crystals should source from day crystals
        week_crystal = Crystal.from_crystals(
            insight="Week",
            significance="",
            principles=[],
            source_crystals=[session.id],  # Wrong level!
            level=CrystalLevel.WEEK,
        )

        with pytest.raises(LevelConsistencyError):
            crystal_store.append(week_crystal)

    def test_recent(self, crystal_store: CrystalStore) -> None:
        """Test getting recent crystals."""
        now = datetime.now()

        for i in range(5):
            c = Crystal.from_crystallization(
                insight=f"Crystal {i}",
                significance="",
                principles=[],
                source_marks=[MarkId(f"mark-{i}")],
                time_range=(now, now),
            )
            crystal_store.append(c)

        recent = crystal_store.recent(limit=3)
        assert len(recent) == 3

    def test_stats(
        self,
        crystal_store: CrystalStore,
        sample_crystal: Crystal,
    ) -> None:
        """Test store statistics."""
        crystal_store.append(sample_crystal)

        stats = crystal_store.stats()

        assert stats["total_crystals"] == 1
        assert stats["by_level"]["SESSION"] == 1


# =============================================================================
# Crystallizer Tests
# =============================================================================


class MockSoul:
    """Mock Soul for testing without LLM."""

    def __init__(self, has_llm: bool = True, response: str = ""):
        self._has_llm = has_llm
        self._response = response

    @property
    def has_llm(self) -> bool:
        return self._has_llm

    async def dialogue(self, message: str, **kwargs: Any) -> Any:
        """Mock dialogue response."""

        class MockResponse:
            response = (
                self._response
                or '{"insight": "Mock insight that is long enough to pass validation", "significance": "Mock significance", "principles": ["composable"], "topics": ["test"], "confidence": 0.9}'
            )

        return MockResponse()


class TestCrystallizer:
    """Tests for the Crystallizer LLM integration."""

    @pytest.mark.asyncio
    async def test_crystallize_marks_with_llm(self, sample_marks: list[Mark]) -> None:
        """Test crystallizing marks with LLM."""
        soul = MockSoul(has_llm=True)
        crystallizer = Crystallizer(soul)

        crystal = await crystallizer.crystallize_marks(sample_marks)

        assert crystal.level == CrystalLevel.SESSION
        assert crystal.insight == "Mock insight that is long enough to pass validation"
        assert crystal.significance == "Mock significance"
        assert "composable" in crystal.principles
        assert len(crystal.source_marks) == 10

    @pytest.mark.asyncio
    async def test_crystallize_marks_without_llm(self, sample_marks: list[Mark]) -> None:
        """Test crystallizing marks with template fallback."""
        soul = MockSoul(has_llm=False)
        crystallizer = Crystallizer(soul)

        crystal = await crystallizer.crystallize_marks(sample_marks)

        assert crystal.level == CrystalLevel.SESSION
        assert "10 actions recorded" in crystal.insight
        assert crystal.confidence == 0.5  # Template confidence

    @pytest.mark.asyncio
    async def test_crystallize_empty_marks_raises(self) -> None:
        """Test that empty marks list raises error."""
        crystallizer = Crystallizer(None)

        with pytest.raises(ValueError, match="empty marks"):
            await crystallizer.crystallize_marks([])

    @pytest.mark.asyncio
    async def test_crystallize_crystals_level_day(self) -> None:
        """Test crystallizing session crystals into day crystal."""
        now = datetime.now()

        # Create session crystals
        session_crystals = []
        for i in range(3):
            c = Crystal.from_crystallization(
                insight=f"Session {i} insight",
                significance=f"Session {i} significance",
                principles=["composable"],
                source_marks=[MarkId(f"mark-{i}")],
                time_range=(now, now + timedelta(hours=i)),
            )
            session_crystals.append(c)

        soul = MockSoul(has_llm=True)
        crystallizer = Crystallizer(soul)

        day_crystal = await crystallizer.crystallize_crystals(
            session_crystals,
            CrystalLevel.DAY,
        )

        assert day_crystal.level == CrystalLevel.DAY
        assert len(day_crystal.source_crystals) == 3

    @pytest.mark.asyncio
    async def test_crystallize_session_level_raises(self) -> None:
        """Test that SESSION level raises for crystal crystallization."""
        crystallizer = Crystallizer(None)

        # Create a dummy crystal to pass non-empty check
        dummy_crystal = Crystal.from_crystallization(
            insight="Dummy",
            significance="",
            principles=[],
            source_marks=[MarkId("mark-1")],
            time_range=(datetime.now(), datetime.now()),
        )

        with pytest.raises(ValueError, match="SESSION"):
            await crystallizer.crystallize_crystals([dummy_crystal], CrystalLevel.SESSION)

    @pytest.mark.asyncio
    async def test_crystallize_wrong_source_level_raises(self) -> None:
        """Test that wrong source level raises error."""
        now = datetime.now()

        # Create a day crystal (level 1)
        day_crystal = Crystal.from_crystals(
            insight="Day",
            significance="",
            principles=[],
            source_crystals=[CrystalId("session-1")],
            level=CrystalLevel.DAY,
        )

        crystallizer = Crystallizer(None)

        # Try to create DAY from DAY (should be from SESSION)
        with pytest.raises(ValueError, match="Expected level SESSION"):
            await crystallizer.crystallize_crystals([day_crystal], CrystalLevel.DAY)

    def test_prompt_formatting(self, sample_marks: list[Mark]) -> None:
        """Test that marks are formatted correctly for prompt."""
        crystallizer = Crystallizer(None)
        formatted = crystallizer._format_marks(sample_marks)

        # Response content is used for formatting
        assert "Did thing 0" in formatted
        assert "[" in formatted  # Timestamp brackets
        assert "tags:" in formatted  # Tags are included

    def test_time_span_formatting(self) -> None:
        """Test time span formatting."""
        crystallizer = Crystallizer(None)
        now = datetime.now()

        # Test hours
        span = crystallizer._format_time_span((now, now + timedelta(hours=2)))
        assert "2h" in span

        # Test minutes
        span = crystallizer._format_time_span((now, now + timedelta(minutes=30)))
        assert "30m" in span

        # Test days
        span = crystallizer._format_time_span((now, now + timedelta(days=1, hours=2)))
        assert "1d" in span

    def test_parse_llm_response_valid(self) -> None:
        """Test parsing valid LLM JSON response."""
        crystallizer = Crystallizer(None)

        response = '{"insight": "This is a valid long enough insight for testing", "significance": "Sig", "principles": ["a"], "topics": ["b"], "confidence": 0.85}'
        result = crystallizer._parse_llm_response(response)

        assert result is not None
        assert result.insight == "This is a valid long enough insight for testing"
        assert result.significance == "Sig"
        assert result.principles == ["a"]
        assert result.topics == ["b"]
        assert result.confidence == 0.85

    def test_parse_llm_response_with_code_fence(self) -> None:
        """Test parsing LLM response wrapped in code fence."""
        crystallizer = Crystallizer(None)

        response = """```json
{"insight": "This is a properly long test insight in markdown", "significance": "", "principles": [], "topics": [], "confidence": 0.8}
```"""
        result = crystallizer._parse_llm_response(response)

        assert result is not None
        assert result.insight == "This is a properly long test insight in markdown"

    def test_parse_llm_response_invalid_json(self) -> None:
        """Test fallback when JSON is invalid."""
        crystallizer = Crystallizer(None)

        response = 'This is not JSON but has "insight": "This is a properly long partial match for testing"'
        result = crystallizer._parse_llm_response(response)

        # Should use regex fallback
        assert result is not None
        assert result.insight == "This is a properly long partial match for testing"
        # Confidence should be penalized for regex extraction
        assert result.confidence == pytest.approx(0.6 * 0.7, rel=0.01)

    def test_parse_llm_response_too_short(self) -> None:
        """Test that too-short insights are rejected."""
        crystallizer = Crystallizer(None)

        response = '{"insight": "short", "significance": "", "principles": [], "topics": [], "confidence": 0.8}'
        result = crystallizer._parse_llm_response(response)

        # Should be rejected due to validation
        assert result is None

    def test_parse_llm_response_error_pattern(self) -> None:
        """Test that error patterns are rejected."""
        crystallizer = Crystallizer(None)

        response = '{"insight": "error: something went wrong here", "significance": "", "principles": [], "topics": [], "confidence": 0.8}'
        result = crystallizer._parse_llm_response(response)

        # Should be rejected due to error pattern
        assert result is None

    def test_parse_llm_response_json_fragment(self) -> None:
        """Test that JSON fragments in insight are rejected."""
        crystallizer = Crystallizer(None)

        response = '{"insight": "{ partial json fragment", "significance": "", "principles": [], "topics": [], "confidence": 0.8}'
        result = crystallizer._parse_llm_response(response)

        # Should be rejected due to JSON fragment
        assert result is None

    def test_parse_llm_response_no_extractable_fields(self) -> None:
        """Test that responses with no extractable fields return None."""
        crystallizer = Crystallizer(None)

        response = "This is just raw text with no JSON structure at all"
        result = crystallizer._parse_llm_response(response)

        # Should return None (no valid extraction)
        assert result is None


# =============================================================================
# Integration Tests
# =============================================================================


class TestCrystalIntegration:
    """Integration tests for the full crystal pipeline."""

    @pytest.mark.asyncio
    async def test_marks_to_crystal_to_store(
        self,
        sample_marks: list[Mark],
        crystal_store: CrystalStore,
    ) -> None:
        """Test the full pipeline: marks → crystal → store."""
        # Crystallize
        soul = MockSoul(has_llm=True)
        crystallizer = Crystallizer(soul)
        crystal = await crystallizer.crystallize_marks(sample_marks, session_id="test")

        # Store
        crystal_store.append(crystal)

        # Retrieve
        retrieved = crystal_store.get(crystal.id)
        assert retrieved is not None
        assert retrieved.insight == "Mock insight that is long enough to pass validation"
        assert retrieved.session_id == "test"

        # Expand
        sources = crystal_store.expand(crystal.id)
        assert len(sources) == 10

    @pytest.mark.asyncio
    async def test_hierarchical_crystallization(self) -> None:
        """Test creating a hierarchy: marks → session → day."""
        now = datetime.now()
        store = CrystalStore()
        soul = MockSoul(has_llm=True)
        crystallizer = Crystallizer(soul)

        # Create session crystals
        session_crystals = []
        for i in range(3):
            marks = [
                Mark(
                    id=MarkId(f"mark-{i}-{j}"),
                    timestamp=now + timedelta(hours=i, minutes=j),
                    origin="test",
                    stimulus=Stimulus(kind="action", content=f"Action {i}-{j}"),
                    response=Response(kind="mark", content=f"Did {i}-{j}"),
                    tags=(),
                    phase=NPhase.ACT,
                )
                for j in range(5)
            ]

            crystal = await crystallizer.crystallize_marks(marks, session_id=f"session-{i}")
            store.append(crystal)
            session_crystals.append(crystal)

        # Create day crystal
        day_crystal = await crystallizer.crystallize_crystals(
            session_crystals,
            CrystalLevel.DAY,
        )
        store.append(day_crystal)

        # Verify hierarchy
        assert len(store) == 4  # 3 session + 1 day
        assert len(store.by_level(CrystalLevel.SESSION)) == 3
        assert len(store.by_level(CrystalLevel.DAY)) == 1

        # Expand day to sessions
        day_sources = store.expand(day_crystal.id)
        assert len(day_sources) == 3
        assert all(isinstance(s, Crystal) for s in day_sources)

        # Expand all the way to marks
        all_marks = store.expand_to_marks(day_crystal.id)
        assert len(all_marks) == 15  # 3 sessions × 5 marks


# =============================================================================
# Property-Based Tests (if hypothesis available)
# =============================================================================

try:
    from hypothesis import given, strategies as st

    class TestCrystalProperties:
        """Property-based tests for Crystal invariants."""

        @given(st.floats(min_value=0.0, max_value=1.0))
        def test_mood_dimensions_in_range(self, value: float) -> None:
            """Test that mood dimensions are always in [0, 1]."""
            mood = MoodVector(warmth=value)
            assert 0.0 <= mood.warmth <= 1.0

        @given(st.floats(min_value=-10.0, max_value=10.0))
        def test_mood_clamping(self, value: float) -> None:
            """Test that out-of-range values are clamped."""
            mood = MoodVector(warmth=value)
            assert 0.0 <= mood.warmth <= 1.0

except ImportError:
    pass  # hypothesis not available


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "TestCrystal",
    "TestCrystalLevel",
    "TestMoodVector",
    "TestCrystalStore",
    "TestCrystallizer",
    "TestCrystalIntegration",
]
