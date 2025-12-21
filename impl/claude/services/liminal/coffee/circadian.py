"""
Circadian Resonance: The garden knows things from yesterday.

Checkpoint 1.1-1.2 of Metabolic Development Protocol.

User Journey:
    $ kg coffee begin

    ☕ Good morning

    💫 This morning echoes December 14th...
       Then, you said: "I want to feel like I'm exploring, not completing."
       That morning, you chose 🎲 SERENDIPITOUS and discovered sheaf coherence.

    📍 FROM YOUR PATTERNS
       "Ship something" appears in 7 of last 10 mornings
       "Depth over breadth" — recurring voice anchor

    🎲 FROM THE VOID (10% serendipity)
       Three weeks ago: "The constraint is the freedom"

The key insight: similar mornings have similar needs.
Match today to past mornings for context and serendipity.

Teaching:
    gotcha: Day-of-week matters more than raw recency.
            Monday mornings resonate with Monday mornings.
            (Evidence: test_circadian.py::test_weekday_resonance)

    gotcha: FOSSIL layer (> 14 days) is the serendipity goldmine.
            Recent voices are too familiar; ancient ones surprise.
            (Evidence: test_circadian.py::test_fossil_serendipity)

AGENTESE: void.metabolism.serendipity, time.coffee.resonance
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import ChallengeLevel, MorningVoice


# =============================================================================
# Stratigraphy Layers (Voice Archaeology)
# =============================================================================


class StratigraphyLayer(Enum):
    """
    Layers in the voice archaeology.

    Like geological strata, older voices are deeper.
    SURFACE: Today and yesterday
    SHALLOW: 2-14 days ago
    FOSSIL: > 14 days ago (the serendipity goldmine)
    """

    SURFACE = auto()  # 0-1 days
    SHALLOW = auto()  # 2-14 days
    FOSSIL = auto()  # > 14 days

    @property
    def age_range(self) -> tuple[int, int | None]:
        """Age range in days (min, max or None for unbounded)."""
        return {
            StratigraphyLayer.SURFACE: (0, 1),
            StratigraphyLayer.SHALLOW: (2, 14),
            StratigraphyLayer.FOSSIL: (15, None),
        }[self]

    @classmethod
    def for_age(cls, days: int) -> "StratigraphyLayer":
        """Get the layer for a given age in days."""
        if days <= 1:
            return cls.SURFACE
        elif days <= 14:
            return cls.SHALLOW
        else:
            return cls.FOSSIL


# =============================================================================
# Archaeological Voice
# =============================================================================


@dataclass(frozen=True)
class ArchaeologicalVoice:
    """
    A voice from the past with archaeological metadata.

    Wraps MorningVoice with layer and age information.
    """

    voice: "MorningVoice"
    layer: StratigraphyLayer
    age_days: int
    weekday: int  # 0=Monday, 6=Sunday

    @classmethod
    def from_voice(cls, voice: "MorningVoice", today: date | None = None) -> "ArchaeologicalVoice":
        """Create from a MorningVoice."""
        today = today or date.today()
        age_days = (today - voice.captured_date).days
        layer = StratigraphyLayer.for_age(age_days)
        weekday = voice.captured_date.weekday()

        return cls(
            voice=voice,
            layer=layer,
            age_days=age_days,
            weekday=weekday,
        )

    @property
    def weekday_name(self) -> str:
        """Human-readable weekday name."""
        return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][
            self.weekday
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "voice": self.voice.to_dict(),
            "layer": self.layer.name,
            "age_days": self.age_days,
            "weekday": self.weekday,
            "weekday_name": self.weekday_name,
        }


# =============================================================================
# Resonance Result
# =============================================================================


@dataclass(frozen=True)
class ResonanceMatch:
    """
    A past morning that resonates with today.

    Includes the voice and why it matched.
    """

    archaeological: ArchaeologicalVoice
    score: float  # 0.0-1.0 resonance score
    reasons: tuple[str, ...]  # Why this matched

    @property
    def voice(self) -> "MorningVoice":
        return self.archaeological.voice

    @property
    def date(self) -> date:
        return self.voice.captured_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "archaeological": self.archaeological.to_dict(),
            "score": round(self.score, 4),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class PatternOccurrence:
    """
    A recurring pattern detected in voice history.

    E.g., "Ship something" appears in 7 of last 10 mornings.
    """

    pattern: str  # The detected pattern
    occurrences: int  # How many times it appeared
    total_voices: int  # Out of how many voices
    recent_dates: tuple[date, ...]  # When it appeared recently

    @property
    def frequency(self) -> float:
        """Frequency as ratio (0.0-1.0)."""
        if self.total_voices == 0:
            return 0.0
        return self.occurrences / self.total_voices

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern": self.pattern,
            "occurrences": self.occurrences,
            "total_voices": self.total_voices,
            "frequency": round(self.frequency, 4),
            "recent_dates": [d.isoformat() for d in self.recent_dates],
        }


@dataclass(frozen=True)
class SerendipityWisdom:
    """
    Unexpected wisdom from the FOSSIL layer.

    Surfaces with 10% probability, always from > 14 days ago.
    """

    archaeological: ArchaeologicalVoice
    quote: str  # The wisdom extracted

    def to_dict(self) -> dict[str, Any]:
        return {
            "archaeological": self.archaeological.to_dict(),
            "quote": self.quote,
        }


@dataclass
class CircadianContext:
    """
    Full circadian context for today's morning.

    Combines resonance, patterns, and optional serendipity.
    """

    today: date
    resonances: list[ResonanceMatch] = field(default_factory=list)
    patterns: list[PatternOccurrence] = field(default_factory=list)
    serendipity: SerendipityWisdom | None = None
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "today": self.today.isoformat(),
            "resonances": [r.to_dict() for r in self.resonances],
            "patterns": [p.to_dict() for p in self.patterns],
            "serendipity": self.serendipity.to_dict() if self.serendipity else None,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# Circadian Resonance Service
# =============================================================================


class CircadianResonance:
    """
    Match today to similar past mornings.

    The core insight: similar mornings have similar needs.
    - Same weekday matters (Monday Kent ≠ Friday Kent)
    - Similar energy/challenge levels resonate
    - Keyword overlap in success_criteria

    Usage:
        resonance = CircadianResonance()

        # Get full context for today
        context = resonance.get_context(voices, today=date.today())

        # Just find resonant mornings
        matches = resonance.find_resonances(voices, limit=3)

        # Check for serendipity (10% chance)
        wisdom = resonance.maybe_serendipity(voices)
    """

    def __init__(
        self,
        serendipity_probability: float = 0.10,
        fossil_age_days: int = 14,
    ):
        """
        Initialize CircadianResonance.

        Args:
            serendipity_probability: Chance of FOSSIL layer wisdom (default 10%)
            fossil_age_days: Days before voice becomes FOSSIL (default 14)
        """
        self._serendipity_prob = serendipity_probability
        self._fossil_age = fossil_age_days

    # =========================================================================
    # Main API
    # =========================================================================

    def get_context(
        self,
        voices: list["MorningVoice"],
        today: date | None = None,
        resonance_limit: int = 3,
        pattern_limit: int = 5,
    ) -> CircadianContext:
        """
        Get full circadian context for today.

        Combines:
        - Resonant mornings (similar past mornings)
        - Recurring patterns (themes across voices)
        - Optional serendipity (10% chance of FOSSIL wisdom)

        Args:
            voices: Historical voice captures
            today: Today's date (default: today)
            resonance_limit: Max resonances to return
            pattern_limit: Max patterns to return

        Returns:
            CircadianContext with all gathered context
        """
        today = today or date.today()

        # Filter out today's voice if present
        historical = [v for v in voices if v.captured_date < today]

        if not historical:
            return CircadianContext(today=today)

        # Find resonances
        resonances = self.find_resonances(historical, today, limit=resonance_limit)

        # Detect patterns
        patterns = self.detect_patterns(historical, limit=pattern_limit)

        # Maybe trigger serendipity
        serendipity = self.maybe_serendipity(historical, today)

        return CircadianContext(
            today=today,
            resonances=resonances,
            patterns=patterns,
            serendipity=serendipity,
        )

    # =========================================================================
    # Resonance Matching
    # =========================================================================

    def find_resonances(
        self,
        voices: list["MorningVoice"],
        today: date | None = None,
        limit: int = 3,
    ) -> list[ResonanceMatch]:
        """
        Find past mornings that resonate with today.

        Scoring factors:
        - Same weekday: +0.3
        - Similar challenge level chosen: +0.2
        - Keyword overlap in success_criteria: +0.0-0.5
        - Age penalty: -0.01 per day (freshness bias for shallow)

        Args:
            voices: Historical voice captures
            today: Today's date
            limit: Maximum matches to return

        Returns:
            Resonant mornings sorted by score
        """
        today = today or date.today()
        today_weekday = today.weekday()

        matches: list[ResonanceMatch] = []

        for voice in voices:
            if voice.captured_date >= today:
                continue

            arch = ArchaeologicalVoice.from_voice(voice, today)
            score, reasons = self._compute_resonance(arch, today_weekday)

            if score > 0.1:  # Minimum threshold
                matches.append(
                    ResonanceMatch(
                        archaeological=arch,
                        score=score,
                        reasons=tuple(reasons),
                    )
                )

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:limit]

    def _compute_resonance(
        self,
        arch: ArchaeologicalVoice,
        today_weekday: int,
    ) -> tuple[float, list[str]]:
        """Compute resonance score and reasons."""
        score = 0.0
        reasons: list[str] = []

        # Same weekday bonus
        if arch.weekday == today_weekday:
            score += 0.3
            reasons.append(f"Same weekday ({arch.weekday_name})")

        # Challenge level (if chosen)
        if arch.voice.chosen_challenge:
            score += 0.15
            reasons.append(
                f"Chose {arch.voice.chosen_challenge.emoji} {arch.voice.chosen_challenge.value}"
            )

        # Success criteria keywords
        if arch.voice.success_criteria:
            # Check for key phrases
            criteria = arch.voice.success_criteria.lower()
            key_phrases = ["ship", "finish", "explore", "understand", "learn", "fix", "depth"]
            matched = [p for p in key_phrases if p in criteria]
            if matched:
                score += 0.1 * len(matched)
                reasons.append(f"Keywords: {', '.join(matched)}")

        # Age adjustment (slight freshness bias for SHALLOW, but FOSSIL is valuable)
        if arch.layer == StratigraphyLayer.SHALLOW:
            score -= arch.age_days * 0.01  # Small penalty for age
        elif arch.layer == StratigraphyLayer.FOSSIL:
            # FOSSIL gets slight boost for nostalgia value
            score += 0.05

        return max(0.0, min(1.0, score)), reasons

    # =========================================================================
    # Pattern Detection
    # =========================================================================

    def detect_patterns(
        self,
        voices: list["MorningVoice"],
        limit: int = 5,
        min_occurrences: int = 2,
    ) -> list[PatternOccurrence]:
        """
        Detect recurring patterns in voice history.

        Looks for repeated phrases and themes without ML.

        Args:
            voices: Historical voice captures
            limit: Maximum patterns to return
            min_occurrences: Minimum times pattern must appear

        Returns:
            Patterns sorted by frequency
        """
        if not voices:
            return []

        # Count phrase occurrences
        phrase_dates: dict[str, list[date]] = {}

        for voice in voices:
            text = self._extract_searchable_text(voice)
            phrases = self._extract_key_phrases(text)

            for phrase in phrases:
                if phrase not in phrase_dates:
                    phrase_dates[phrase] = []
                phrase_dates[phrase].append(voice.captured_date)

        # Build patterns
        patterns: list[PatternOccurrence] = []
        for phrase, dates in phrase_dates.items():
            if len(dates) >= min_occurrences:
                patterns.append(
                    PatternOccurrence(
                        pattern=phrase,
                        occurrences=len(dates),
                        total_voices=len(voices),
                        recent_dates=tuple(sorted(dates, reverse=True)[:5]),
                    )
                )

        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns[:limit]

    def _extract_searchable_text(self, voice: "MorningVoice") -> str:
        """Extract all searchable text from a voice."""
        parts = []
        if voice.success_criteria:
            parts.append(voice.success_criteria)
        if voice.eye_catch:
            parts.append(voice.eye_catch)
        if voice.non_code_thought:
            parts.append(voice.non_code_thought)
        if voice.raw_feeling:
            parts.append(voice.raw_feeling)
        return " ".join(parts).lower()

    def _extract_key_phrases(self, text: str) -> list[str]:
        """
        Extract key phrases from text.

        Simple approach: look for known important phrases.
        """
        key_phrases = [
            "ship something",
            "depth over breadth",
            "finish",
            "explore",
            "understand",
            "learn",
            "fix",
            "refactor",
            "tasteful",
            "magical",
            "joy",
            "fun",
        ]

        found = []
        for phrase in key_phrases:
            if phrase in text:
                found.append(phrase)

        return found

    # =========================================================================
    # Serendipity (The Accursed Share)
    # =========================================================================

    def maybe_serendipity(
        self,
        voices: list["MorningVoice"],
        today: date | None = None,
    ) -> SerendipityWisdom | None:
        """
        Maybe return unexpected wisdom from the FOSSIL layer.

        10% probability by default. Only samples from voices > 14 days old.

        Args:
            voices: Historical voice captures
            today: Today's date

        Returns:
            SerendipityWisdom if triggered and available, else None
        """
        # Roll the dice
        if random.random() > self._serendipity_prob:
            return None

        today = today or date.today()

        # Filter to FOSSIL layer only
        fossils = [
            ArchaeologicalVoice.from_voice(v, today)
            for v in voices
            if (today - v.captured_date).days > self._fossil_age
        ]

        if not fossils:
            return None

        # Pick a random fossil with substantive content
        substantive = [f for f in fossils if f.voice.is_substantive]
        if not substantive:
            return None

        chosen = random.choice(substantive)
        quote = self._extract_wisdom_quote(chosen.voice)

        return SerendipityWisdom(
            archaeological=chosen,
            quote=quote,
        )

    def _extract_wisdom_quote(self, voice: "MorningVoice") -> str:
        """Extract a quotable piece of wisdom from a voice."""
        # Prefer success_criteria as it's the most intentional
        if voice.success_criteria:
            return voice.success_criteria

        # Fallback to other fields
        if voice.non_code_thought:
            return voice.non_code_thought

        if voice.eye_catch:
            return voice.eye_catch

        if voice.raw_feeling:
            return voice.raw_feeling

        return "No words remain, but the intention lingers."

    def force_serendipity(
        self,
        voices: list["MorningVoice"],
        today: date | None = None,
    ) -> SerendipityWisdom | None:
        """
        Force serendipity trigger (for testing).

        Same as maybe_serendipity but ignores probability.
        """
        today = today or date.today()

        fossils = [
            ArchaeologicalVoice.from_voice(v, today)
            for v in voices
            if (today - v.captured_date).days > self._fossil_age
        ]

        if not fossils:
            return None

        substantive = [f for f in fossils if f.voice.is_substantive]
        if not substantive:
            return None

        chosen = random.choice(substantive)
        quote = self._extract_wisdom_quote(chosen.voice)

        return SerendipityWisdom(
            archaeological=chosen,
            quote=quote,
        )


# =============================================================================
# Factory
# =============================================================================


_resonance: CircadianResonance | None = None


def get_circadian_resonance() -> CircadianResonance:
    """Get or create the global CircadianResonance service."""
    global _resonance
    if _resonance is None:
        _resonance = CircadianResonance()
    return _resonance


def set_circadian_resonance(resonance: CircadianResonance) -> None:
    """Set the global CircadianResonance service (for testing)."""
    global _resonance
    _resonance = resonance


def reset_circadian_resonance() -> None:
    """Reset the global CircadianResonance service."""
    global _resonance
    _resonance = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Stratigraphy
    "StratigraphyLayer",
    "ArchaeologicalVoice",
    # Results
    "ResonanceMatch",
    "PatternOccurrence",
    "SerendipityWisdom",
    "CircadianContext",
    # Service
    "CircadianResonance",
    "get_circadian_resonance",
    "set_circadian_resonance",
    "reset_circadian_resonance",
]
