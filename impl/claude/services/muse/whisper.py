"""
Whisper Engine for The Muse.

Handles generation, timing, and delivery of contextual suggestions.
The Muse whispers—never shouts.

Key Principles:
1. ONE AT A TIME: Never multiple suggestions
2. TIMING MATTERS: Surface during pauses, not mid-flow
3. DISMISSAL MEMORY: Don't repeat dismissed patterns
4. EARNED ENCOURAGEMENT: Praise only after genuine progress

See: plans/witness-muse-implementation.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncGenerator

from .arc import ArcPhase, StoryArc

if TYPE_CHECKING:
    pass


# =============================================================================
# Suggestion Categories
# =============================================================================


class SuggestionCategory(Enum):
    """Categories of Muse suggestions."""

    ENCOURAGEMENT = auto()  # "You're doing great"
    REFRAME = auto()  # "What if you tried..."
    OBSERVATION = auto()  # "I notice you've been..."
    RITUAL = auto()  # "Time for a break?"
    TECHNICAL = auto()  # Specific technical suggestion
    NARRATIVE = auto()  # Story arc observation


# =============================================================================
# Suggestion
# =============================================================================


@dataclass(frozen=True)
class Suggestion:
    """
    A potential suggestion from The Muse.

    Suggestions have confidence and urgency scores that
    determine if/when they surface.
    """

    content: str
    category: SuggestionCategory
    confidence: float  # How sure this is helpful [0, 1]
    urgency: float  # How soon to surface [0, 1]
    context_hash: str = ""  # For dismissal memory
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def should_surface(self) -> bool:
        """Should this suggestion be surfaced?"""
        # High confidence + high urgency = surface
        return self.confidence > 0.5 and self.urgency > 0.3

    @property
    def is_stale(self) -> bool:
        """Is this suggestion too old?"""
        age = datetime.now() - self.created_at
        return age > timedelta(minutes=10)


# =============================================================================
# Whisper (Delivered Suggestion)
# =============================================================================


@dataclass(frozen=True)
class Whisper:
    """
    A delivered suggestion.

    Contains the suggestion content plus metadata for tracking.
    """

    whisper_id: str
    content: str
    category: SuggestionCategory
    confidence: float
    urgency: float
    delivered_at: datetime = field(default_factory=datetime.now)
    arc_phase: ArcPhase = ArcPhase.EXPOSITION
    tension: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage/transmission."""
        return {
            "whisper_id": self.whisper_id,
            "content": self.content,
            "category": self.category.name,
            "confidence": self.confidence,
            "urgency": self.urgency,
            "delivered_at": self.delivered_at.isoformat(),
            "arc_phase": self.arc_phase.name,
            "tension": self.tension,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Whisper:
        """Deserialize from storage."""
        return cls(
            whisper_id=data["whisper_id"],
            content=data["content"],
            category=SuggestionCategory[data["category"]],
            confidence=data["confidence"],
            urgency=data["urgency"],
            delivered_at=datetime.fromisoformat(data["delivered_at"]),
            arc_phase=ArcPhase[data["arc_phase"]],
            tension=data.get("tension", 0.0),
        )


# =============================================================================
# Dismissal Memory
# =============================================================================


@dataclass
class DismissalMemory:
    """
    Remembers what suggestions were dismissed.

    Prevents repeating patterns the user doesn't find helpful.
    Uses context hashes to generalize beyond exact content.
    """

    dismissed_hashes: set[str] = field(default_factory=set)
    dismissed_categories: dict[SuggestionCategory, int] = field(default_factory=dict)
    last_dismissal: datetime | None = None
    total_dismissals: int = 0

    MAX_MEMORY = 100
    CATEGORY_THRESHOLD = 3  # Dismiss a category after 3 rejections

    def record_dismissal(self, suggestion: Suggestion) -> None:
        """Record a dismissed suggestion."""
        self.dismissed_hashes.add(suggestion.context_hash)
        self.total_dismissals += 1
        self.last_dismissal = datetime.now()

        # Track category dismissals
        count = self.dismissed_categories.get(suggestion.category, 0)
        self.dismissed_categories[suggestion.category] = count + 1

        # Bound memory
        if len(self.dismissed_hashes) > self.MAX_MEMORY:
            # Remove oldest (convert to list, remove first items)
            to_remove = len(self.dismissed_hashes) - self.MAX_MEMORY
            for hash in list(self.dismissed_hashes)[:to_remove]:
                self.dismissed_hashes.discard(hash)

    def is_dismissed(self, suggestion: Suggestion) -> bool:
        """Check if a suggestion pattern was dismissed."""
        # Check exact hash
        if suggestion.context_hash in self.dismissed_hashes:
            return True

        # Check category threshold
        category_count = self.dismissed_categories.get(suggestion.category, 0)
        if category_count >= self.CATEGORY_THRESHOLD:
            return True

        return False

    def reset_category(self, category: SuggestionCategory) -> None:
        """Reset dismissal count for a category."""
        self.dismissed_categories[category] = 0

    def decay(self) -> None:
        """Apply time-based decay to dismissal memory."""
        # Categories decay after no dismissals for a while
        for category in list(self.dismissed_categories.keys()):
            self.dismissed_categories[category] = max(0, self.dismissed_categories[category] - 1)


# =============================================================================
# Whisper Engine
# =============================================================================


class WhisperEngine:
    """
    Engine for generating and timing whispers.

    Manages:
    - Suggestion generation based on context
    - Timing (when to surface)
    - Dismissal memory (what not to repeat)
    """

    def __init__(self) -> None:
        self.dismissals = DismissalMemory()
        self._pending: Suggestion | None = None
        self._last_whisper_time: datetime | None = None
        self._whisper_count = 0

        # Cooldown between whispers
        self.min_interval = timedelta(minutes=5)

    def generate_suggestion(self, arc: StoryArc, tension: float) -> Suggestion | None:
        """
        Generate a suggestion based on current arc and tension.

        Returns None if no good suggestion is available.
        """
        import hashlib

        # Generate context hash for dismissal matching
        context = f"{arc.phase.name}:{tension:.1f}"
        context_hash = hashlib.md5(context.encode()).hexdigest()[:8]

        # Select category and content based on arc phase
        if arc.phase == ArcPhase.EXPOSITION:
            suggestion = Suggestion(
                content="Take your time understanding. Good foundations matter more than speed.",
                category=SuggestionCategory.OBSERVATION,
                confidence=0.6,
                urgency=0.2,
                context_hash=context_hash,
            )
        elif arc.phase == ArcPhase.RISING_ACTION:
            if tension > 0.6:
                suggestion = Suggestion(
                    content="The complexity is growing. Consider a small commit to checkpoint progress.",
                    category=SuggestionCategory.TECHNICAL,
                    confidence=0.7,
                    urgency=0.5,
                    context_hash=context_hash,
                )
            else:
                suggestion = Suggestion(
                    content="You're building momentum. Trust the process.",
                    category=SuggestionCategory.ENCOURAGEMENT,
                    confidence=0.6,
                    urgency=0.3,
                    context_hash=context_hash,
                )
        elif arc.phase == ArcPhase.CLIMAX:
            suggestion = Suggestion(
                content="This is the crux. Stay focused—you've got this.",
                category=SuggestionCategory.ENCOURAGEMENT,
                confidence=0.8,
                urgency=0.7,
                context_hash=context_hash,
            )
        elif arc.phase == ArcPhase.FALLING_ACTION:
            suggestion = Suggestion(
                content="The hard part's done. Now it's about polish and clarity.",
                category=SuggestionCategory.OBSERVATION,
                confidence=0.7,
                urgency=0.4,
                context_hash=context_hash,
            )
        else:  # DENOUEMENT
            suggestion = Suggestion(
                content="Nice work. Take a moment to appreciate what you built.",
                category=SuggestionCategory.ENCOURAGEMENT,
                confidence=0.8,
                urgency=0.6,
                context_hash=context_hash,
            )

        # Check dismissal memory
        if self.dismissals.is_dismissed(suggestion):
            return None

        return suggestion

    def should_deliver(self, suggestion: Suggestion) -> bool:
        """Check if a suggestion should be delivered now."""
        # Check cooldown
        if self._last_whisper_time is not None:
            elapsed = datetime.now() - self._last_whisper_time
            if elapsed < self.min_interval:
                return False

        # Check thresholds
        return suggestion.should_surface and not suggestion.is_stale

    def deliver(self, suggestion: Suggestion, arc: StoryArc) -> Whisper:
        """
        Deliver a suggestion as a whisper.

        Records the delivery for tracking.
        """
        import uuid

        whisper = Whisper(
            whisper_id=f"whisper-{uuid.uuid4().hex[:8]}",
            content=suggestion.content,
            category=suggestion.category,
            confidence=suggestion.confidence,
            urgency=suggestion.urgency,
            arc_phase=arc.phase,
            tension=arc.tension,
        )

        self._last_whisper_time = datetime.now()
        self._whisper_count += 1
        self._pending = None

        return whisper

    def record_dismissal(self, whisper: Whisper) -> None:
        """Record that a whisper was dismissed."""
        # Create equivalent suggestion for dismissal tracking
        suggestion = Suggestion(
            content=whisper.content,
            category=whisper.category,
            confidence=whisper.confidence,
            urgency=whisper.urgency,
            context_hash=f"whisper:{whisper.whisper_id}",
        )
        self.dismissals.record_dismissal(suggestion)

    def record_acceptance(self, whisper: Whisper) -> None:
        """Record that a whisper was accepted."""
        # Positive signal for this category
        category = whisper.category
        # Decay dismissal count for accepted categories
        if category in self.dismissals.dismissed_categories:
            self.dismissals.dismissed_categories[category] = max(
                0, self.dismissals.dismissed_categories[category] - 1
            )

    @property
    def stats(self) -> dict[str, Any]:
        """Return engine statistics."""
        return {
            "whisper_count": self._whisper_count,
            "dismissal_count": self.dismissals.total_dismissals,
            "last_whisper": self._last_whisper_time.isoformat()
            if self._last_whisper_time
            else None,
            "categories_suppressed": [
                cat.name
                for cat, count in self.dismissals.dismissed_categories.items()
                if count >= self.dismissals.CATEGORY_THRESHOLD
            ],
        }

    async def whisper_stream(
        self,
        arc_provider: "AsyncGenerator[StoryArc, None] | None" = None,
        poll_interval: float = 30.0,
    ) -> AsyncGenerator[Whisper, None]:
        """
        Stream whispers in real-time via async generator.

        AGENTESE: self.muse.stream (SSE)

        Yields whispers as they become appropriate to surface based on
        arc phase and tension. Respects min_interval between whispers.

        Args:
            arc_provider: Optional async generator providing story arc updates.
                         If None, uses a static default arc.
            poll_interval: Seconds between checks (default 30.0)

        Yields:
            Whisper objects as they become available
        """
        # Default arc if no provider
        current_arc = StoryArc()

        while True:
            try:
                # Generate suggestion based on current arc
                suggestion = self.generate_suggestion(current_arc, current_arc.tension)

                if suggestion and self.should_deliver(suggestion):
                    whisper = self.deliver(suggestion, current_arc)
                    yield whisper

                # Wait before next check
                await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                # Clean shutdown
                break
            except Exception:
                # Continue on errors
                await asyncio.sleep(poll_interval)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SuggestionCategory",
    "Suggestion",
    "Whisper",
    "DismissalMemory",
    "WhisperEngine",
]
