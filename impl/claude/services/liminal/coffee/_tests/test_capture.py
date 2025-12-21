"""
Tests for Morning Coffee Voice Capture.

Verifies:
- CaptureSession manages multi-question flow
- Voice persistence (save/load)
- Voice anchor generation
- Pattern extraction from history
"""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from services.liminal.coffee.capture import (
    CAPTURE_QUESTIONS,
    CaptureQuestion,
    CaptureSession,
    extract_voice_patterns,
    get_voice_store_path,
    iter_all_voices,
    load_recent_voices,
    load_voice,
    save_voice,
    voice_to_anchor,
)
from services.liminal.coffee.types import (
    ChallengeLevel,
    MorningVoice,
)

# =============================================================================
# Capture Question Tests
# =============================================================================


class TestCaptureQuestions:
    """Tests for capture questions structure."""

    def test_has_four_questions(self) -> None:
        """Should have 4 capture questions."""
        assert len(CAPTURE_QUESTIONS) == 4

    def test_success_criteria_is_required(self) -> None:
        """success_criteria question should be required."""
        success_q = next(q for q in CAPTURE_QUESTIONS if q.key == "success_criteria")
        assert success_q.required is True

    def test_all_have_prompts(self) -> None:
        """All questions have prompts and placeholders."""
        for q in CAPTURE_QUESTIONS:
            assert q.prompt
            assert q.placeholder
            assert q.key


# =============================================================================
# Capture Session Tests
# =============================================================================


class TestCaptureSession:
    """Tests for CaptureSession flow."""

    def test_starts_at_first_question(self) -> None:
        """Session starts at index 0."""
        session = CaptureSession()

        assert session.current_index == 0
        assert session.current_question is not None
        assert session.current_question.key == "non_code_thought"

    def test_answer_advances_question(self) -> None:
        """Answering advances to next question."""
        session = CaptureSession()
        first_key = session.current_question.key

        next_q = session.answer("My answer")

        assert session.answers.get(first_key) == "My answer"
        assert next_q is not None
        assert next_q.key != first_key

    def test_skip_advances_with_none(self) -> None:
        """Skipping records None and advances."""
        session = CaptureSession()
        first_key = session.current_question.key

        session.skip()

        assert session.answers.get(first_key) is None
        assert session.current_index == 1

    def test_is_complete_after_all_answers(self) -> None:
        """Session is complete after all questions answered."""
        session = CaptureSession()

        for _ in range(len(CAPTURE_QUESTIONS)):
            session.answer("answer")

        assert session.is_complete is True
        assert session.current_question is None

    def test_progress_updates(self) -> None:
        """Progress increases as questions are answered."""
        session = CaptureSession()

        assert session.progress == 0.0

        session.answer("a")
        assert 0.0 < session.progress < 1.0

        for _ in range(len(CAPTURE_QUESTIONS) - 1):
            session.answer("a")

        assert session.progress == 1.0

    def test_build_voice_returns_morning_voice(self) -> None:
        """build_voice creates MorningVoice from answers."""
        session = CaptureSession()
        session.answers = {
            "non_code_thought": "Had a dream",
            "success_criteria": "Ship it",
        }
        session.chosen_challenge = ChallengeLevel.FOCUSED

        voice = session.build_voice()

        assert isinstance(voice, MorningVoice)
        assert voice.non_code_thought == "Had a dream"
        assert voice.success_criteria == "Ship it"
        assert voice.chosen_challenge == ChallengeLevel.FOCUSED

    def test_build_voice_incomplete_session(self) -> None:
        """build_voice works even for incomplete sessions."""
        session = CaptureSession()
        session.answer("First answer")
        # Don't complete all questions

        voice = session.build_voice()

        assert isinstance(voice, MorningVoice)
        assert voice.non_code_thought == "First answer"
        assert voice.success_criteria is None

    def test_to_dict_serializes(self) -> None:
        """to_dict creates serializable dict."""
        session = CaptureSession()
        session.answer("answer")
        session.chosen_challenge = ChallengeLevel.GENTLE

        data = session.to_dict()

        assert "captured_date" in data
        assert "answers" in data
        assert "current_index" in data
        assert data["chosen_challenge"] == "gentle"

    def test_completed_at_set_on_completion(self) -> None:
        """completed_at is set when session completes."""
        session = CaptureSession()

        assert session.completed_at is None

        for _ in range(len(CAPTURE_QUESTIONS)):
            session.answer("a")

        assert session.completed_at is not None


# =============================================================================
# Voice Persistence Tests
# =============================================================================


class TestVoiceStore:
    """Tests for voice persistence."""

    def test_get_voice_store_path_creates_dir(self, tmp_path: Path) -> None:
        """get_voice_store_path creates directory if needed."""
        store = get_voice_store_path(tmp_path / "new" / "store")

        assert store.exists()
        assert store.is_dir()

    def test_save_voice_creates_file(self, tmp_path: Path) -> None:
        """save_voice creates JSON file."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship it",
        )

        filepath = save_voice(voice, tmp_path)

        assert filepath.exists()
        assert filepath.name == "2025-12-21.json"

    def test_save_voice_content(self, tmp_path: Path) -> None:
        """save_voice writes correct content."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            non_code_thought="Dreams",
            success_criteria="Ship it",
        )

        filepath = save_voice(voice, tmp_path)

        with open(filepath) as f:
            data = json.load(f)

        assert data["captured_date"] == "2025-12-21"
        assert data["non_code_thought"] == "Dreams"
        assert data["success_criteria"] == "Ship it"

    def test_load_voice_returns_voice(self, tmp_path: Path) -> None:
        """load_voice loads saved voice."""
        original = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship it",
        )
        save_voice(original, tmp_path)

        loaded = load_voice(date(2025, 12, 21), tmp_path)

        assert loaded is not None
        assert loaded.captured_date == original.captured_date
        assert loaded.success_criteria == original.success_criteria

    def test_load_voice_missing_returns_none(self, tmp_path: Path) -> None:
        """load_voice returns None for missing file."""
        loaded = load_voice(date(2025, 1, 1), tmp_path)
        assert loaded is None

    def test_load_recent_voices(self, tmp_path: Path) -> None:
        """load_recent_voices returns sorted list."""
        dates = [date(2025, 12, 19), date(2025, 12, 20), date(2025, 12, 21)]
        for d in dates:
            save_voice(MorningVoice(captured_date=d), tmp_path)

        voices = load_recent_voices(limit=10, store_path=tmp_path)

        assert len(voices) == 3
        # Should be newest first
        assert voices[0].captured_date == date(2025, 12, 21)
        assert voices[2].captured_date == date(2025, 12, 19)

    def test_load_recent_voices_respects_limit(self, tmp_path: Path) -> None:
        """load_recent_voices respects limit."""
        for day in range(1, 10):
            save_voice(
                MorningVoice(captured_date=date(2025, 12, day)),
                tmp_path,
            )

        voices = load_recent_voices(limit=3, store_path=tmp_path)

        assert len(voices) == 3

    def test_iter_all_voices(self, tmp_path: Path) -> None:
        """iter_all_voices yields all voices."""
        dates = [date(2025, 12, 19), date(2025, 12, 20)]
        for d in dates:
            save_voice(MorningVoice(captured_date=d), tmp_path)

        voices = list(iter_all_voices(tmp_path))

        assert len(voices) == 2
        # Should be oldest first
        assert voices[0].captured_date == date(2025, 12, 19)


# =============================================================================
# Voice Anchor Tests
# =============================================================================


class TestVoiceToAnchor:
    """Tests for voice_to_anchor."""

    def test_with_success_criteria(self) -> None:
        """Returns anchor if success_criteria present."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship the feature",
        )

        anchor = voice_to_anchor(voice)

        assert anchor is not None
        assert anchor["text"] == "Ship the feature"
        assert anchor["source"] == "morning_coffee"

    def test_without_success_criteria(self) -> None:
        """Returns None if no success_criteria."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            non_code_thought="Just a thought",
        )

        anchor = voice_to_anchor(voice)

        assert anchor is None


# =============================================================================
# Pattern Extraction Tests
# =============================================================================


class TestExtractVoicePatterns:
    """Tests for extract_voice_patterns."""

    def test_empty_voices(self) -> None:
        """Empty list returns minimal patterns."""
        patterns = extract_voice_patterns([])

        assert patterns["count"] == 0

    def test_counts_voices(self) -> None:
        """Counts total voices."""
        voices = [MorningVoice(captured_date=date(2025, 12, i)) for i in range(1, 6)]

        patterns = extract_voice_patterns(voices)

        assert patterns["count"] == 5

    def test_counts_substantive(self) -> None:
        """Counts substantive voices."""
        voices = [
            MorningVoice(
                captured_date=date(2025, 12, 1),
                success_criteria="Ship it",
            ),
            MorningVoice(captured_date=date(2025, 12, 2)),  # Not substantive
        ]

        patterns = extract_voice_patterns(voices)

        assert patterns["substantive_count"] == 1

    def test_counts_challenge_preferences(self) -> None:
        """Counts challenge level preferences."""
        voices = [
            MorningVoice(
                captured_date=date(2025, 12, 1),
                chosen_challenge=ChallengeLevel.GENTLE,
            ),
            MorningVoice(
                captured_date=date(2025, 12, 2),
                chosen_challenge=ChallengeLevel.GENTLE,
            ),
            MorningVoice(
                captured_date=date(2025, 12, 3),
                chosen_challenge=ChallengeLevel.FOCUSED,
            ),
        ]

        patterns = extract_voice_patterns(voices)

        assert patterns["challenge_preferences"]["gentle"] == 2
        assert patterns["challenge_preferences"]["focused"] == 1

    def test_extracts_common_themes(self) -> None:
        """Extracts common words from success criteria."""
        voices = [
            MorningVoice(
                captured_date=date(2025, 12, 1),
                success_criteria="Ship the feature today",
            ),
            MorningVoice(
                captured_date=date(2025, 12, 2),
                success_criteria="Ship another feature",
            ),
        ]

        patterns = extract_voice_patterns(voices)

        # "ship" and "feature" should appear twice
        assert "ship" in patterns["common_themes"]
        assert "feature" in patterns["common_themes"]


# =============================================================================
# MorningVoice Type Tests
# =============================================================================


class TestMorningVoiceType:
    """Tests for MorningVoice dataclass."""

    def test_is_substantive_with_content(self) -> None:
        """is_substantive True when has content."""
        voice = MorningVoice(
            captured_date=date.today(),
            success_criteria="Ship it",
        )
        assert voice.is_substantive is True

    def test_not_substantive_when_empty(self) -> None:
        """is_substantive False when empty."""
        voice = MorningVoice(captured_date=date.today())
        assert voice.is_substantive is False

    def test_from_dict_round_trip(self) -> None:
        """to_dict and from_dict are inverses."""
        original = MorningVoice(
            captured_date=date(2025, 12, 21),
            non_code_thought="Dreams",
            eye_catch="The garden",
            success_criteria="Ship it",
            raw_feeling="Energized",
            chosen_challenge=ChallengeLevel.FOCUSED,
        )

        data = original.to_dict()
        restored = MorningVoice.from_dict(data)

        assert restored.captured_date == original.captured_date
        assert restored.non_code_thought == original.non_code_thought
        assert restored.eye_catch == original.eye_catch
        assert restored.success_criteria == original.success_criteria
        assert restored.raw_feeling == original.raw_feeling
        assert restored.chosen_challenge == original.chosen_challenge

    def test_from_dict_missing_date_defaults_today(self) -> None:
        """from_dict uses today if date missing."""
        data = {"success_criteria": "Ship it"}
        voice = MorningVoice.from_dict(data)

        assert voice.captured_date == date.today()
