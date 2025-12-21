"""
Voice Capture: What's on your mind before code takes over?

Movement 4 of the Morning Coffee ritual. Records Kent's authentic
morning state — the anti-sausage goldmine.

Kent at 8am after rest ≠ Kent at 11pm after 6 hours of debugging.
Morning Kent is closer to the "vision holder."

Captures become voice anchors for future anti-sausage checks.

Patterns Applied:
- Container Owns Workflow (Pattern 1): CoffeeService owns CaptureSession

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

from .types import (
    ChallengeLevel,
    MorningVoice,
)

# =============================================================================
# Capture Questions
# =============================================================================


@dataclass(frozen=True)
class CaptureQuestion:
    """A question in the voice capture flow."""

    key: str  # Field name in MorningVoice
    prompt: str  # Display prompt
    placeholder: str  # Example/placeholder text
    required: bool = False  # Is this question required?


# The capture questions (order matters)
CAPTURE_QUESTIONS: tuple[CaptureQuestion, ...] = (
    CaptureQuestion(
        key="non_code_thought",
        prompt="What's on your mind that has nothing to do with code?",
        placeholder="Dreams, ideas, something from breakfast, a feeling...",
        required=False,
    ),
    CaptureQuestion(
        key="eye_catch",
        prompt="Looking at the garden view, what catches your eye?",
        placeholder="A file, a pattern, something that sparked curiosity...",
        required=False,
    ),
    CaptureQuestion(
        key="success_criteria",
        prompt="What would make today feel like a good day?",
        placeholder="Ship one feature, understand the problem, have fun...",
        required=True,  # This is the voice anchor source
    ),
    CaptureQuestion(
        key="raw_feeling",
        prompt="Any other thoughts? (optional)",
        placeholder="Energy level, mood, anything else...",
        required=False,
    ),
)


# =============================================================================
# Capture Session
# =============================================================================


@dataclass
class CaptureSession:
    """
    A voice capture session.

    Manages the multi-question flow and builds MorningVoice.
    Not frozen because it accumulates answers during the session.
    """

    captured_date: date = field(default_factory=date.today)
    answers: dict[str, str | None] = field(default_factory=dict)
    current_index: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    chosen_challenge: ChallengeLevel | None = None

    @property
    def questions(self) -> tuple[CaptureQuestion, ...]:
        """Get the capture questions."""
        return CAPTURE_QUESTIONS

    @property
    def current_question(self) -> CaptureQuestion | None:
        """Get the current question, or None if complete."""
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    @property
    def is_complete(self) -> bool:
        """Check if all questions have been answered."""
        return self.current_index >= len(self.questions)

    @property
    def progress(self) -> float:
        """Progress through questions (0.0-1.0)."""
        return self.current_index / len(self.questions)

    def answer(self, response: str | None) -> CaptureQuestion | None:
        """
        Record answer to current question and advance.

        Returns the next question, or None if complete.
        """
        question = self.current_question
        if question is None:
            return None

        # Store answer (None or empty string both work)
        self.answers[question.key] = response if response else None

        # Advance
        self.current_index += 1

        # Mark complete if done
        if self.is_complete:
            self.completed_at = datetime.now()

        return self.current_question

    def skip(self) -> CaptureQuestion | None:
        """Skip current question (record as None)."""
        return self.answer(None)

    def build_voice(self) -> MorningVoice:
        """
        Build MorningVoice from captured answers.

        Can be called even if session is incomplete.
        """
        return MorningVoice(
            captured_date=self.captured_date,
            non_code_thought=self.answers.get("non_code_thought"),
            eye_catch=self.answers.get("eye_catch"),
            success_criteria=self.answers.get("success_criteria"),
            raw_feeling=self.answers.get("raw_feeling"),
            chosen_challenge=self.chosen_challenge,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize session state."""
        return {
            "captured_date": self.captured_date.isoformat(),
            "answers": self.answers,
            "current_index": self.current_index,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "chosen_challenge": self.chosen_challenge.value if self.chosen_challenge else None,
        }


# =============================================================================
# Voice Persistence
# =============================================================================


def get_voice_store_path(
    base_path: Path | str | None = None,
) -> Path:
    """Get path to voice capture store."""
    if base_path is None:
        # Default to XDG data home
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        base_path = Path(xdg_data) / "kgents" / "morning-coffee"

    path = Path(base_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_voice(
    voice: MorningVoice,
    store_path: Path | str | None = None,
) -> Path:
    """
    Save a MorningVoice capture to persistent storage.

    Returns path to saved file.
    """
    store = get_voice_store_path(store_path)

    # Filename: YYYY-MM-DD.json
    filename = f"{voice.captured_date.isoformat()}.json"
    filepath = store / filename

    # Save as JSON
    with open(filepath, "w") as f:
        json.dump(voice.to_dict(), f, indent=2)

    return filepath


def load_voice(
    capture_date: date,
    store_path: Path | str | None = None,
) -> MorningVoice | None:
    """
    Load a MorningVoice capture from storage.

    Returns None if not found.
    """
    store = get_voice_store_path(store_path)

    filename = f"{capture_date.isoformat()}.json"
    filepath = store / filename

    if not filepath.exists():
        return None

    with open(filepath) as f:
        data = json.load(f)

    return MorningVoice.from_dict(data)


def load_recent_voices(
    limit: int = 7,
    store_path: Path | str | None = None,
) -> list[MorningVoice]:
    """
    Load recent voice captures.

    Returns list sorted by date descending (newest first).
    """
    store = get_voice_store_path(store_path)

    voices: list[MorningVoice] = []

    # Get all json files, sorted by name (date) descending
    json_files = sorted(store.glob("*.json"), reverse=True)

    for filepath in json_files[:limit]:
        try:
            with open(filepath) as f:
                data = json.load(f)
            voices.append(MorningVoice.from_dict(data))
        except (json.JSONDecodeError, KeyError):
            # Skip malformed files
            continue

    return voices


def iter_all_voices(
    store_path: Path | str | None = None,
) -> Iterator[MorningVoice]:
    """
    Iterate over all voice captures.

    Yields MorningVoice in date order (oldest first).
    """
    store = get_voice_store_path(store_path)

    for filepath in sorted(store.glob("*.json")):
        try:
            with open(filepath) as f:
                data = json.load(f)
            yield MorningVoice.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            continue


# =============================================================================
# Voice Anchor Integration
# =============================================================================


def voice_to_anchor(voice: MorningVoice) -> dict[str, Any] | None:
    """
    Convert MorningVoice to voice anchor format.

    Voice anchors are used by the anti-sausage protocol.
    Returns None if voice isn't substantive enough.
    """
    return voice.as_voice_anchor()


def extract_voice_patterns(
    voices: list[MorningVoice],
) -> dict[str, Any]:
    """
    Extract patterns from historical voice captures.

    Useful for understanding Kent's morning voice over time.
    """
    if not voices:
        return {"count": 0, "patterns": []}

    # Count challenge level preferences
    challenge_counts: dict[str, int] = {}
    for voice in voices:
        if voice.chosen_challenge:
            key = voice.chosen_challenge.value
            challenge_counts[key] = challenge_counts.get(key, 0) + 1

    # Count substantive captures
    substantive_count = sum(1 for v in voices if v.is_substantive)

    # Find common words in success criteria
    common_words: dict[str, int] = {}
    for voice in voices:
        if voice.success_criteria:
            words = voice.success_criteria.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    common_words[word] = common_words.get(word, 0) + 1

    # Sort by frequency
    top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "count": len(voices),
        "substantive_count": substantive_count,
        "challenge_preferences": challenge_counts,
        "common_themes": [word for word, _ in top_words],
    }


# =============================================================================
# Async Variants
# =============================================================================


async def save_voice_async(
    voice: MorningVoice,
    store_path: Path | str | None = None,
) -> Path:
    """Async version of save_voice."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: save_voice(voice, store_path),
    )


async def load_voice_async(
    capture_date: date,
    store_path: Path | str | None = None,
) -> MorningVoice | None:
    """Async version of load_voice."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: load_voice(capture_date, store_path),
    )


async def load_recent_voices_async(
    limit: int = 7,
    store_path: Path | str | None = None,
) -> list[MorningVoice]:
    """Async version of load_recent_voices."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: load_recent_voices(limit, store_path),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Questions
    "CaptureQuestion",
    "CAPTURE_QUESTIONS",
    # Session
    "CaptureSession",
    # Persistence
    "get_voice_store_path",
    "save_voice",
    "load_voice",
    "load_recent_voices",
    "iter_all_voices",
    # Integration
    "voice_to_anchor",
    "extract_voice_patterns",
    # Async
    "save_voice_async",
    "load_voice_async",
    "load_recent_voices_async",
]
