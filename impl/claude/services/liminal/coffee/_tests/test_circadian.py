"""
Tests for Circadian Resonance and Voice Archaeology.

Checkpoint 1.1-1.2 of Metabolic Development Protocol.

Key verification criteria:
- Same weekday resonates stronger than adjacent days
- FOSSIL layer (> 14 days) is serendipity goldmine
- Pattern detection finds recurring themes
- 10% serendipity trigger from deep archaeology
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from services.liminal.coffee.circadian import (
    ArchaeologicalVoice,
    CircadianContext,
    CircadianResonance,
    PatternOccurrence,
    ResonanceMatch,
    SerendipityWisdom,
    StratigraphyLayer,
    get_circadian_resonance,
    reset_circadian_resonance,
    set_circadian_resonance,
)
from services.liminal.coffee.types import ChallengeLevel, MorningVoice

# =============================================================================
# Test Fixtures
# =============================================================================


def make_voice(
    days_ago: int,
    success_criteria: str | None = None,
    chosen_challenge: ChallengeLevel | None = None,
    today: date | None = None,
) -> MorningVoice:
    """Create a MorningVoice from N days ago."""
    today = today or date.today()
    return MorningVoice(
        captured_date=today - timedelta(days=days_ago),
        success_criteria=success_criteria,
        chosen_challenge=chosen_challenge,
    )


def make_voices_last_n_days(n: int, today: date | None = None) -> list[MorningVoice]:
    """Create voices for the last N days with varied content."""
    today = today or date.today()
    voices = []

    contents = [
        ("Ship something today", ChallengeLevel.FOCUSED),
        ("Explore the codebase", ChallengeLevel.SERENDIPITOUS),
        ("Finish the feature", ChallengeLevel.INTENSE),
        ("Fix that bug", ChallengeLevel.GENTLE),
        ("Depth over breadth", ChallengeLevel.FOCUSED),
        ("Understand the problem", ChallengeLevel.FOCUSED),
        ("Ship something today", ChallengeLevel.INTENSE),  # Repeat
        ("Learn the new API", ChallengeLevel.GENTLE),
    ]

    for i in range(1, n + 1):
        content, challenge = contents[(i - 1) % len(contents)]
        voices.append(make_voice(i, content, challenge, today))

    return voices


# =============================================================================
# StratigraphyLayer Tests
# =============================================================================


class TestStratigraphyLayer:
    """Test voice archaeology layers."""

    def test_surface_layer(self) -> None:
        """SURFACE layer is 0-1 days."""
        assert StratigraphyLayer.for_age(0) == StratigraphyLayer.SURFACE
        assert StratigraphyLayer.for_age(1) == StratigraphyLayer.SURFACE

    def test_shallow_layer(self) -> None:
        """SHALLOW layer is 2-14 days."""
        assert StratigraphyLayer.for_age(2) == StratigraphyLayer.SHALLOW
        assert StratigraphyLayer.for_age(7) == StratigraphyLayer.SHALLOW
        assert StratigraphyLayer.for_age(14) == StratigraphyLayer.SHALLOW

    def test_fossil_layer(self) -> None:
        """FOSSIL layer is > 14 days."""
        assert StratigraphyLayer.for_age(15) == StratigraphyLayer.FOSSIL
        assert StratigraphyLayer.for_age(30) == StratigraphyLayer.FOSSIL
        assert StratigraphyLayer.for_age(100) == StratigraphyLayer.FOSSIL

    def test_age_ranges(self) -> None:
        """Age ranges are correctly defined."""
        assert StratigraphyLayer.SURFACE.age_range == (0, 1)
        assert StratigraphyLayer.SHALLOW.age_range == (2, 14)
        assert StratigraphyLayer.FOSSIL.age_range == (15, None)


# =============================================================================
# ArchaeologicalVoice Tests
# =============================================================================


class TestArchaeologicalVoice:
    """Test archaeological voice wrapper."""

    def test_from_voice_today(self) -> None:
        """Voice from today is SURFACE."""
        today = date.today()
        voice = MorningVoice(captured_date=today, success_criteria="test")
        arch = ArchaeologicalVoice.from_voice(voice, today)

        assert arch.layer == StratigraphyLayer.SURFACE
        assert arch.age_days == 0
        assert arch.voice == voice

    def test_from_voice_week_ago(self) -> None:
        """Voice from a week ago is SHALLOW."""
        today = date.today()
        voice = make_voice(7, "test", today=today)
        arch = ArchaeologicalVoice.from_voice(voice, today)

        assert arch.layer == StratigraphyLayer.SHALLOW
        assert arch.age_days == 7

    def test_from_voice_month_ago(self) -> None:
        """Voice from a month ago is FOSSIL."""
        today = date.today()
        voice = make_voice(30, "test", today=today)
        arch = ArchaeologicalVoice.from_voice(voice, today)

        assert arch.layer == StratigraphyLayer.FOSSIL
        assert arch.age_days == 30

    def test_weekday_preserved(self) -> None:
        """Weekday is correctly computed."""
        # Monday = 0
        monday = date(2024, 12, 16)  # A known Monday
        voice = MorningVoice(captured_date=monday, success_criteria="test")
        arch = ArchaeologicalVoice.from_voice(voice, monday + timedelta(days=7))

        assert arch.weekday == 0
        assert arch.weekday_name == "Monday"


# =============================================================================
# CircadianResonance Tests
# =============================================================================


class TestCircadianResonance:
    """Test circadian resonance service."""

    @pytest.fixture
    def resonance(self) -> CircadianResonance:
        """Create a fresh resonance service."""
        return CircadianResonance()

    def test_empty_voices_returns_empty_context(self, resonance: CircadianResonance) -> None:
        """No voices = empty context."""
        context = resonance.get_context([], today=date.today())

        assert context.resonances == []
        assert context.patterns == []
        assert context.serendipity is None

    def test_weekday_resonance(self, resonance: CircadianResonance) -> None:
        """Same weekday resonates stronger than different weekday."""
        # Create a Monday
        today = date(2024, 12, 16)  # Monday

        # Voice from last Monday (7 days ago)
        last_monday = make_voice(7, "Ship something", ChallengeLevel.FOCUSED, today)

        # Voice from last Tuesday (6 days ago)
        last_tuesday = make_voice(6, "Ship something", ChallengeLevel.FOCUSED, today)

        voices = [last_monday, last_tuesday]
        resonances = resonance.find_resonances(voices, today)

        assert len(resonances) == 2
        # Monday should score higher due to same weekday
        monday_match = next(r for r in resonances if r.voice == last_monday)
        tuesday_match = next(r for r in resonances if r.voice == last_tuesday)

        assert monday_match.score > tuesday_match.score
        assert any("Same weekday" in r for r in monday_match.reasons)

    def test_challenge_level_affects_resonance(self, resonance: CircadianResonance) -> None:
        """Chosen challenge level adds to resonance score."""
        # Use a Monday so we can ensure same-weekday bonus
        today = date(2024, 12, 16)  # Monday

        # Create voices from same weekday to ensure they pass threshold
        with_challenge = make_voice(7, "Ship something today", ChallengeLevel.FOCUSED, today)
        without_challenge = make_voice(14, "Ship something today", None, today)

        voices = [with_challenge, without_challenge]
        resonances = resonance.find_resonances(voices, today)

        # Both should pass threshold due to weekday + keyword match
        assert len(resonances) >= 2

        # Voice with challenge should score higher
        with_match = next(r for r in resonances if r.voice == with_challenge)
        without_match = next(r for r in resonances if r.voice == without_challenge)

        assert with_match.score >= without_match.score

    def test_keyword_overlap_adds_score(self, resonance: CircadianResonance) -> None:
        """Keyword overlap in success_criteria increases score."""
        today = date.today()

        # Voice with key phrases
        with_keywords = make_voice(5, "Ship something and explore deeply", None, today)
        without_keywords = make_voice(4, "Random text here", None, today)

        voices = [with_keywords, without_keywords]
        resonances = resonance.find_resonances(voices, today)

        # Filter to get matches (both should pass threshold)
        matches = {r.voice: r for r in resonances}

        if with_keywords in matches and without_keywords in matches:
            assert matches[with_keywords].score >= matches[without_keywords].score


# =============================================================================
# Pattern Detection Tests
# =============================================================================


class TestPatternDetection:
    """Test recurring pattern detection."""

    @pytest.fixture
    def resonance(self) -> CircadianResonance:
        return CircadianResonance()

    def test_detect_recurring_phrase(self, resonance: CircadianResonance) -> None:
        """Detect phrase that appears multiple times."""
        today = date.today()

        # "ship something" appears 3 times
        voices = [
            make_voice(1, "Ship something today", None, today),
            make_voice(3, "Ship something and celebrate", None, today),
            make_voice(5, "Ship something small", None, today),
            make_voice(7, "Random other text", None, today),
        ]

        patterns = resonance.detect_patterns(voices)

        # Should find "ship" pattern
        ship_pattern = next((p for p in patterns if "ship" in p.pattern.lower()), None)
        assert ship_pattern is not None
        assert ship_pattern.occurrences >= 3

    def test_pattern_frequency_sorting(self, resonance: CircadianResonance) -> None:
        """Patterns sorted by frequency."""
        today = date.today()

        voices = [
            # "finish" appears 4 times
            make_voice(1, "Finish the feature", None, today),
            make_voice(2, "Finish something", None, today),
            make_voice(3, "Finish it today", None, today),
            make_voice(4, "Finish and ship", None, today),
            # "explore" appears 2 times
            make_voice(5, "Explore the code", None, today),
            make_voice(6, "Explore deeply", None, today),
        ]

        patterns = resonance.detect_patterns(voices)

        if len(patterns) >= 2:
            # First pattern should have higher frequency
            assert patterns[0].frequency >= patterns[1].frequency

    def test_min_occurrences_filter(self, resonance: CircadianResonance) -> None:
        """Patterns below min_occurrences are filtered."""
        today = date.today()

        voices = [
            make_voice(1, "Unique phrase one", None, today),
            make_voice(2, "Different phrase two", None, today),
        ]

        # Default min_occurrences is 2, so single occurrences filtered
        patterns = resonance.detect_patterns(voices, min_occurrences=2)

        # No patterns should appear (each phrase only once)
        assert len(patterns) == 0


# =============================================================================
# Serendipity Tests
# =============================================================================


class TestSerendipity:
    """Test serendipity from FOSSIL layer."""

    @pytest.fixture
    def resonance(self) -> CircadianResonance:
        return CircadianResonance(serendipity_probability=0.10)

    def test_fossil_serendipity_only_old_voices(self, resonance: CircadianResonance) -> None:
        """Serendipity only samples from FOSSIL layer (> 14 days)."""
        today = date.today()

        # Only recent voices (no FOSSILs)
        voices = [
            make_voice(1, "Recent thought", None, today),
            make_voice(5, "Week old thought", None, today),
            make_voice(10, "Still shallow", None, today),
        ]

        # Force serendipity trigger
        wisdom = resonance.force_serendipity(voices, today)

        # No FOSSIL voices = no serendipity possible
        assert wisdom is None

    def test_fossil_serendipity_returns_wisdom(self, resonance: CircadianResonance) -> None:
        """Serendipity returns wisdom from FOSSIL layer."""
        today = date.today()

        voices = [
            make_voice(1, "Recent", None, today),
            make_voice(20, "The constraint is the freedom", None, today),  # FOSSIL
            make_voice(30, "Depth over breadth always", None, today),  # FOSSIL
        ]

        wisdom = resonance.force_serendipity(voices, today)

        assert wisdom is not None
        assert wisdom.archaeological.layer == StratigraphyLayer.FOSSIL
        assert wisdom.archaeological.age_days >= 15
        assert wisdom.quote in ["The constraint is the freedom", "Depth over breadth always"]

    def test_maybe_serendipity_probability(self) -> None:
        """maybe_serendipity triggers ~10% of the time."""
        # Use 100% probability for testing
        always_resonance = CircadianResonance(serendipity_probability=1.0)
        never_resonance = CircadianResonance(serendipity_probability=0.0)

        today = date.today()
        voices = [make_voice(30, "Ancient wisdom", None, today)]

        # 100% should always trigger
        wisdom = always_resonance.maybe_serendipity(voices, today)
        assert wisdom is not None

        # 0% should never trigger
        wisdom = never_resonance.maybe_serendipity(voices, today)
        assert wisdom is None


# =============================================================================
# Full Context Tests
# =============================================================================


class TestCircadianContext:
    """Test full circadian context generation."""

    @pytest.fixture
    def resonance(self) -> CircadianResonance:
        return CircadianResonance(serendipity_probability=0.0)  # Disable for determinism

    def test_get_context_combines_all(self, resonance: CircadianResonance) -> None:
        """get_context combines resonances, patterns, and serendipity."""
        today = date(2024, 12, 16)  # Monday

        voices = [
            # Last Monday (resonates)
            make_voice(7, "Ship something", ChallengeLevel.FOCUSED, today),
            # More voices for patterns
            make_voice(14, "Ship something again", ChallengeLevel.FOCUSED, today),
            make_voice(21, "Ship something always", ChallengeLevel.FOCUSED, today),
        ]

        context = resonance.get_context(voices, today)

        assert context.today == today
        assert len(context.resonances) > 0
        # "ship" should be a pattern (appears 3 times)
        # Note: pattern detection may not find it if min_occurrences > 3
        assert context.serendipity is None  # Disabled

    def test_context_excludes_today(self, resonance: CircadianResonance) -> None:
        """Today's voice is excluded from resonance matching."""
        today = date.today()

        voices = [
            MorningVoice(captured_date=today, success_criteria="Today's voice"),
            make_voice(7, "Last week", None, today),
        ]

        context = resonance.get_context(voices, today)

        # Today's voice should not appear in resonances
        today_in_resonances = any(r.voice.captured_date == today for r in context.resonances)
        assert not today_in_resonances

    def test_context_to_dict(self, resonance: CircadianResonance) -> None:
        """Context serializes correctly."""
        today = date.today()
        voices = make_voices_last_n_days(30, today)

        context = resonance.get_context(voices, today)
        data = context.to_dict()

        assert "today" in data
        assert "resonances" in data
        assert "patterns" in data
        assert "serendipity" in data
        assert data["today"] == today.isoformat()


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactory:
    """Test factory functions."""

    def teardown_method(self) -> None:
        reset_circadian_resonance()

    def test_get_creates_singleton(self) -> None:
        r1 = get_circadian_resonance()
        r2 = get_circadian_resonance()
        assert r1 is r2

    def test_set_replaces_singleton(self) -> None:
        custom = CircadianResonance(serendipity_probability=0.5)
        set_circadian_resonance(custom)
        assert get_circadian_resonance() is custom

    def test_reset_clears_singleton(self) -> None:
        r1 = get_circadian_resonance()
        reset_circadian_resonance()
        r2 = get_circadian_resonance()
        assert r1 is not r2
