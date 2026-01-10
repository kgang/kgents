"""
Daily Lab: Trail-to-Crystal Pilot for the Constitutional Decision OS.

This module implements the daily journaling and crystallization workflow,
validating the Constitutional Decision OS through personal use.

AGENTESE Paths:
- witness.daily_lab.manifest    - Daily lab status overview
- witness.daily_lab.capture     - Capture a new mark (quick, tagged, or with reasoning)
- witness.daily_lab.trail       - Get today's trail of marks
- witness.daily_lab.crystallize - Create a crystal from today's marks
- witness.daily_lab.export      - Export the day's work

Joy Calibration:
    Primary: FLOW - "Lighter than a to-do list"
    Secondary: WARMTH - "Kind companion reviewing your day"

Philosophy:
    "Witnessing accelerates, not slows."
    "System is descriptive, not punitive."

The Daily Lab provides:
- DailyMark: Low-friction mark capture with WARMTH calibration
- Trail: Sequential mark navigation by date range
- DailyCrystal: L0 -> L1 -> L2 -> L3 compression with honesty disclosure
- Export: Shareable artifacts with warm, personal tone

Amendment G Compliance:
    COMPRESSION_HONESTY: Every crystal discloses what was dropped.

See: plans/enlightened-synthesis/04-joy-integration.md
See: pilots/trail-to-crystal-daily-lab.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator, Literal

from protocols.agentese.contract import Contract, Response as ContractResponse
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node

from .crystal import Crystal, CrystalId, CrystalLevel, MoodVector, generate_crystal_id
from .crystal_store import CrystalStore, get_crystal_store
from .honesty import (
    CompressionHonesty as HonestyCompressionHonesty,
    CrystalHonestyCalculator,
    get_honesty_calculator,
)
from .mark import (
    ConstitutionalAlignment,
    Mark,
    MarkId,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)
from .trace_store import MarkStore, get_mark_store

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger("kgents.witness.daily_lab")


# =============================================================================
# Mark Tags (From Requirements)
# =============================================================================


class DailyTag(str, Enum):
    """Tags for daily mark capture.

    Each tag captures a different kind of moment:
    - EUREKA: A breakthrough or insight
    - GOTCHA: Something that tripped you up
    - TASTE: A design or aesthetic decision
    - FRICTION: Resistance or difficulty encountered
    - JOY: A moment of delight
    - VETO: Something that felt wrong (Mirror Test)
    """

    EUREKA = "eureka"  # Breakthrough
    GOTCHA = "gotcha"  # Trap avoided or fallen into
    TASTE = "taste"  # Aesthetic decision
    FRICTION = "friction"  # Resistance encountered
    JOY = "joy"  # Delight moment
    VETO = "veto"  # Mirror Test failure


# =============================================================================
# WARMTH-Calibrated Prompts
# =============================================================================


WARMTH_PROMPTS = {
    "capture_quick": "What's on your mind?",
    "capture_with_tag": "Let's note that {tag} moment.",
    "capture_reasoning": "What made this stand out to you?",
    "day_review": "Let's look back at your day together.",
    "week_review": "Here's what emerged over the week.",
    "crystal_intro": "I noticed some patterns worth keeping.",
    "compression_honest": "To keep this clear, I'm setting aside: {dropped}",
    "no_marks_found": "A quiet day. That's okay too.",
    "export_header": "Here's what we captured together",
}


WARMTH_RESPONSES = {
    "mark_captured": "Got it.",
    "mark_captured_with_feeling": "That sounds like a {tag} moment. Noted.",
    "crystal_created": "I've crystallized the key insights for you.",
    "nothing_to_compress": "Not enough yet to crystallize. Let's keep going.",
    "export_ready": "Here's a snapshot you can share.",
}


# =============================================================================
# DailyMark: Low-Friction Capture
# =============================================================================


@dataclass
class DailyMark:
    """
    A daily mark with WARMTH calibration.

    DailyMark wraps the core Mark with a warmer, more personal interface
    suited for daily journaling. It emphasizes:
    - Low friction (defaults for everything except content)
    - Personal tone (tags that map to feelings)
    - Optional reasoning (only when you want to reflect)
    """

    content: str
    tag: DailyTag | None = None
    reasoning: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    # Internal mark reference
    _mark: Mark | None = None

    @property
    def mark(self) -> Mark:
        """Get or create the underlying Mark."""
        if self._mark is None:
            tags = (self.tag.value,) if self.tag else ()

            stimulus = Stimulus(
                kind="daily_note",
                content=self.content,
                source="daily_lab",
                metadata={"reasoning": self.reasoning} if self.reasoning else {},
            )

            response = Response(
                kind="thought",
                content=self.content,
                success=True,
                metadata={"tag": self.tag.value if self.tag else None},
            )

            self._mark = Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                domain="journal",
                stimulus=stimulus,
                response=response,
                umwelt=UmweltSnapshot.witness(trust_level=1),
                timestamp=self.timestamp,
                tags=tags,
            )

        return self._mark

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "tag": self.tag.value if self.tag else None,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "mark_id": str(self.mark.id),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DailyMark:
        """Create from dictionary."""
        tag = DailyTag(data["tag"]) if data.get("tag") else None
        return cls(
            content=data["content"],
            tag=tag,
            reasoning=data.get("reasoning"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class DailyMarkCapture:
    """
    WARMTH-calibrated mark capture interface.

    This is the primary entry point for daily mark capture.
    It provides a warm, low-friction interface for quick notes.
    """

    def __init__(self, store: MarkStore | None = None):
        # Use 'is not None' instead of 'or' because empty MarkStore is falsy
        self._store = store if store is not None else get_mark_store()

    def quick(self, content: str) -> DailyMark:
        """
        Capture a quick mark without any ceremony.

        This is the lowest-friction capture path.
        Just say what's on your mind.

        WARMTH: "{content}" -> "Got it."
        """
        daily_mark = DailyMark(content=content)
        self._store.append(daily_mark.mark)
        logger.info(f"Quick mark captured: {content[:50]}...")
        return daily_mark

    def tagged(self, content: str, tag: DailyTag) -> DailyMark:
        """
        Capture a mark with a feeling tag.

        Use this when you know what kind of moment it was.

        WARMTH: "That sounds like a {tag} moment. Noted."
        """
        daily_mark = DailyMark(content=content, tag=tag)
        self._store.append(daily_mark.mark)
        logger.info(f"Tagged mark captured: [{tag.value}] {content[:50]}...")
        return daily_mark

    def with_reasoning(
        self,
        content: str,
        reasoning: str,
        tag: DailyTag | None = None,
    ) -> DailyMark:
        """
        Capture a mark with reasoning for deeper reflection.

        Use this when you want to note WHY something mattered.

        WARMTH: "What made this stand out to you?"
        """
        daily_mark = DailyMark(content=content, tag=tag, reasoning=reasoning)
        self._store.append(daily_mark.mark)
        logger.info(f"Reasoned mark captured: {content[:50]}...")
        return daily_mark

    def eureka(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture a breakthrough moment."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.EUREKA)
            if reasoning
            else self.tagged(content, DailyTag.EUREKA)
        )

    def gotcha(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture something that tripped you up."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.GOTCHA)
            if reasoning
            else self.tagged(content, DailyTag.GOTCHA)
        )

    def taste(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture a design or aesthetic decision."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.TASTE)
            if reasoning
            else self.tagged(content, DailyTag.TASTE)
        )

    def friction(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture resistance encountered."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.FRICTION)
            if reasoning
            else self.tagged(content, DailyTag.FRICTION)
        )

    def joy(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture a moment of delight."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.JOY)
            if reasoning
            else self.tagged(content, DailyTag.JOY)
        )

    def veto(self, content: str, reasoning: str | None = None) -> DailyMark:
        """Capture a Mirror Test failure."""
        return (
            self.with_reasoning(content, reasoning, DailyTag.VETO)
            if reasoning
            else self.tagged(content, DailyTag.VETO)
        )

    def prompt(self) -> str:
        """Get the capture prompt (WARMTH calibrated)."""
        return WARMTH_PROMPTS["capture_quick"]

    def warmth_response(
        self,
        warmth: float = 0.5,
        surprise: float = 0.3,
        flow: float = 0.6,
        trigger: str = "mark capture",
    ) -> str:
        """
        Generate a warmth-calibrated response using the JoyFunctor.

        This method uses the TRAIL_TO_CRYSTAL_JOY functor to observe
        joy signals and generate an appropriate warm response.

        Joy is INFERRED from behavioral signals, never interrogated.
        The user is not asked "was that joyful?" - we observe and respond.

        Args:
            warmth: Warmth signal [0, 1], e.g., collaboration vs. transaction
            surprise: Surprise signal [0, 1], e.g., serendipity vs. predictability
            flow: Flow signal [0, 1], e.g., effortless vs. laborious
            trigger: What caused this joy observation

        Returns:
            A warm, human-friendly response string

        Example:
            >>> capture = DailyMarkCapture()
            >>> capture.warmth_response(warmth=0.8, flow=0.7, trigger="eureka moment")
            "That felt like a real moment of connection."
        """
        from .joy import TRAIL_TO_CRYSTAL_JOY, warmth_response as joy_warmth_response

        # Observe joy using the trail-to-crystal calibrated functor
        joy_obs = TRAIL_TO_CRYSTAL_JOY.observe(
            observer="daily_lab_user",
            warmth=warmth,
            surprise=surprise,
            flow=flow,
            trigger=trigger,
        )

        # Generate warm response based on observation
        return joy_warmth_response(joy_obs)


# =============================================================================
# Trail: Sequential Navigation
# =============================================================================


@dataclass
class TrailPosition:
    """Current position in a trail of marks."""

    marks: list[Mark]
    index: int = 0

    @property
    def current(self) -> Mark | None:
        """Get current mark."""
        if not self.marks or self.index < 0 or self.index >= len(self.marks):
            return None
        return self.marks[self.index]

    @property
    def has_next(self) -> bool:
        """Check if there's a next mark."""
        return self.index < len(self.marks) - 1

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous mark."""
        return self.index > 0

    @property
    def total(self) -> int:
        """Total marks in trail."""
        return len(self.marks)

    @property
    def position(self) -> int:
        """Current 1-indexed position."""
        return self.index + 1 if self.marks else 0


class Trail:
    """
    Sequential navigation through marks by date range.

    The Trail provides a linear view of marks for review,
    with filtering by date, tag, and importance.

    WARMTH: "Let's look back at your day together."
    """

    def __init__(self, store: MarkStore | None = None):
        # Use 'is not None' instead of 'or' because empty MarkStore is falsy
        self._store = store if store is not None else get_mark_store()

    def for_date(self, target_date: date) -> TrailPosition:
        """Get marks for a specific date."""
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        return self.for_range(start, end)

    def for_today(self) -> TrailPosition:
        """Get marks for today."""
        return self.for_date(date.today())

    def for_range(
        self,
        start: datetime,
        end: datetime,
        tags: list[DailyTag] | None = None,
    ) -> TrailPosition:
        """Get marks for a date range, optionally filtered by tags."""
        marks = []

        for mark in self._store.all():
            # Filter by time range
            if mark.timestamp < start or mark.timestamp > end:
                continue

            # Filter by origin (only daily_lab marks)
            if mark.origin != "daily_lab":
                continue

            # Filter by tags if specified
            if tags:
                tag_values = [t.value for t in tags]
                if not any(t in mark.tags for t in tag_values):
                    continue

            marks.append(mark)

        # Sort by timestamp (oldest first for chronological review)
        marks.sort(key=lambda m: m.timestamp)

        return TrailPosition(marks=marks)

    def for_week(self, week_start: date | None = None) -> TrailPosition:
        """Get marks for a week."""
        if week_start is None:
            # Start from Monday of current week
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        start = datetime.combine(week_start, datetime.min.time())
        end = start + timedelta(days=7)

        return self.for_range(start, end)

    def navigate(
        self, position: TrailPosition, direction: Literal["next", "prev"]
    ) -> TrailPosition:
        """Navigate within a trail."""
        new_index = position.index
        if direction == "next" and position.has_next:
            new_index += 1
        elif direction == "prev" and position.has_prev:
            new_index -= 1

        return TrailPosition(marks=position.marks, index=new_index)

    def filter_by_importance(self, position: TrailPosition) -> TrailPosition:
        """Filter to only important marks (eureka, veto, taste)."""
        important_tags = {DailyTag.EUREKA.value, DailyTag.VETO.value, DailyTag.TASTE.value}
        filtered = [m for m in position.marks if any(t in important_tags for t in m.tags)]
        return TrailPosition(marks=filtered)


# =============================================================================
# DailyCrystal: Compression with Honesty
# =============================================================================


@dataclass
class CompressionHonesty:
    """
    Disclosure of what was dropped during compression.

    Amendment G: COMPRESSION_HONESTY
    Every crystal MUST disclose what was dropped.

    Note: This is a backward-compatible wrapper. The full implementation
    with WARMTH-calibrated messages is in honesty.py (HonestyCompressionHonesty).
    """

    dropped_count: int
    dropped_tags: list[str]
    dropped_summaries: list[str]  # Brief descriptions of dropped content
    galois_loss: float  # Semantic drift measure
    warm_disclosure: str = ""  # WARMTH-calibrated message (Amendment G)
    preserved_ratio: float = 1.0  # What percentage was kept

    def to_disclosure(self) -> str:
        """Generate human-readable disclosure."""
        # Prefer warm disclosure if available
        if self.warm_disclosure:
            return self.warm_disclosure

        # Fallback to original format
        if self.dropped_count == 0:
            return "Everything was preserved."

        parts = [f"Set aside {self.dropped_count} notes"]
        if self.dropped_tags:
            parts.append(f"(mostly {', '.join(self.dropped_tags)})")
        parts.append(f"to keep this focused (drift: {self.galois_loss:.1%})")

        return " ".join(parts)

    @classmethod
    def from_honesty_module(
        cls, honesty: HonestyCompressionHonesty, dropped_count: int
    ) -> "CompressionHonesty":
        """Create from honesty module's CompressionHonesty."""
        return cls(
            dropped_count=dropped_count,
            dropped_tags=honesty.dropped_tags,
            dropped_summaries=honesty.dropped_summaries,
            galois_loss=honesty.galois_loss,
            warm_disclosure=honesty.warm_disclosure,
            preserved_ratio=honesty.preserved_ratio,
        )


@dataclass
class DailyCrystal:
    """
    A crystal with compression honesty disclosure.

    DailyCrystal wraps the core Crystal with Amendment G compliance,
    ensuring we're honest about what was dropped during compression.

    WARMTH: "I noticed some patterns worth keeping."
    """

    crystal: Crystal
    honesty: CompressionHonesty
    level: CrystalLevel

    @property
    def insight(self) -> str:
        """The core insight."""
        return self.crystal.insight

    @property
    def significance(self) -> str:
        """Why this matters."""
        return self.crystal.significance

    @property
    def disclosure(self) -> str:
        """What was dropped (Amendment G)."""
        return self.honesty.to_disclosure()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "crystal": self.crystal.to_dict(),
            "honesty": {
                "dropped_count": self.honesty.dropped_count,
                "dropped_tags": self.honesty.dropped_tags,
                "dropped_summaries": self.honesty.dropped_summaries,
                "galois_loss": self.honesty.galois_loss,
            },
            "level": self.level.value,
            "disclosure": self.disclosure,
        }


class DailyCrystallizer:
    """
    Create crystals from daily marks with honesty disclosure.

    The crystallizer compresses marks into crystals at different levels:
    - L0 (SESSION): Session marks -> session crystal
    - L1 (DAY): Day's marks -> daily crystal
    - L2 (WEEK): Week's crystals -> weekly crystal
    - L3 (EPOCH): Monthly/thematic crystals

    Amendment G Compliance:
        Uses CrystalHonestyCalculator for proper Galois loss computation
        and WARMTH-calibrated disclosure messages.

    WARMTH: "To keep this clear, I'm setting aside: {dropped}"
    """

    # Compression thresholds
    MIN_MARKS_FOR_CRYSTAL = 3
    MAX_IMPORTANT_MARKS = 7  # Keep the 7 most important

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        crystal_store: CrystalStore | None = None,
        honesty_calculator: CrystalHonestyCalculator | None = None,
    ):
        # Use 'is not None' instead of 'or' because empty stores are falsy
        self._mark_store = mark_store if mark_store is not None else get_mark_store()
        self._crystal_store = crystal_store if crystal_store is not None else get_crystal_store()
        self._honesty_calculator = (
            honesty_calculator if honesty_calculator is not None else get_honesty_calculator()
        )

    def crystallize_day(self, target_date: date) -> DailyCrystal | None:
        """
        Create a daily crystal (L1) from the day's marks.

        Returns None if there aren't enough marks to crystallize.
        """
        trail = Trail(self._mark_store)
        position = trail.for_date(target_date)

        if position.total < self.MIN_MARKS_FOR_CRYSTAL:
            logger.info(
                f"Not enough marks to crystallize ({position.total} < {self.MIN_MARKS_FOR_CRYSTAL})"
            )
            return None

        return self._compress_marks(
            marks=position.marks,
            level=CrystalLevel.DAY,
            time_range=(
                datetime.combine(target_date, datetime.min.time()),
                datetime.combine(target_date, datetime.max.time()),
            ),
        )

    def crystallize_week(self, week_start: date | None = None) -> DailyCrystal | None:
        """
        Create a weekly crystal (L2) from the week's daily crystals.
        """
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        # Get marks for the whole week
        trail = Trail(self._mark_store)
        position = trail.for_week(week_start)

        if position.total < self.MIN_MARKS_FOR_CRYSTAL:
            logger.info(f"Not enough marks for weekly crystal ({position.total})")
            return None

        week_end = week_start + timedelta(days=6)
        return self._compress_marks(
            marks=position.marks,
            level=CrystalLevel.WEEK,
            time_range=(
                datetime.combine(week_start, datetime.min.time()),
                datetime.combine(week_end, datetime.max.time()),
            ),
        )

    def _compress_marks(
        self,
        marks: list[Mark],
        level: CrystalLevel,
        time_range: tuple[datetime, datetime],
    ) -> DailyCrystal:
        """
        Compress marks into a crystal with honesty disclosure.

        Uses CrystalHonestyCalculator for Amendment G compliance:
        - Proper Galois loss computation
        - WARMTH-calibrated disclosure messages
        """
        import asyncio

        # Prioritize marks by importance
        importance_order = [
            DailyTag.VETO.value,  # Mirror Test failures are most important
            DailyTag.EUREKA.value,  # Breakthroughs next
            DailyTag.TASTE.value,  # Design decisions
            DailyTag.JOY.value,  # Delight moments
            DailyTag.GOTCHA.value,  # Traps
            DailyTag.FRICTION.value,  # Resistance
        ]

        def mark_priority(mark: Mark) -> int:
            for i, tag in enumerate(importance_order):
                if tag in mark.tags:
                    return i
            return len(importance_order)  # Untagged marks last

        sorted_marks = sorted(marks, key=mark_priority)

        # Keep the most important marks
        kept_marks = sorted_marks[: self.MAX_IMPORTANT_MARKS]
        dropped_marks = sorted_marks[self.MAX_IMPORTANT_MARKS :]

        # Generate crystal content from kept marks
        insight = self._generate_insight(kept_marks, level)
        significance = self._generate_significance(kept_marks, level)
        principles = self._extract_principles(kept_marks)
        topics = self._extract_topics(kept_marks)
        mood = MoodVector.from_marks(kept_marks)

        # Create the crystal first (needed for honesty computation)
        # Note: For daily lab, we keep all crystals at SESSION level since we're
        # compressing marks directly. The 'level' parameter is used for semantic
        # labeling (DAY, WEEK) but the Crystal structure uses SESSION to satisfy
        # the Law 3 constraint (only SESSION can have source_marks without source_crystals).
        crystal = Crystal.from_crystallization(
            insight=insight,
            significance=significance,
            principles=principles,
            source_marks=[MarkId(str(m.id)) for m in kept_marks],
            time_range=time_range,
            confidence=0.8,  # Will be updated based on Galois loss
            topics=topics,
            mood=mood,
        )

        # Compute honesty disclosure using CrystalHonestyCalculator (Amendment G)
        try:
            # Run async computation in sync context
            try:
                loop = asyncio.get_running_loop()
                # Already in async context - create task
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._honesty_calculator.compute_honesty(
                            original_marks=marks,
                            crystal=crystal,
                            kept_marks=kept_marks,
                        ),
                    )
                    honesty_result = future.result()
            except RuntimeError:
                # No running loop, safe to create one
                honesty_result = asyncio.run(
                    self._honesty_calculator.compute_honesty(
                        original_marks=marks,
                        crystal=crystal,
                        kept_marks=kept_marks,
                    )
                )

            # Convert from honesty module format to local format
            honesty = CompressionHonesty.from_honesty_module(
                honesty_result,
                dropped_count=len(dropped_marks),
            )
            galois_loss = honesty.galois_loss

        except Exception as e:
            # Fallback to simple heuristic if calculator fails
            logger.warning(f"Honesty calculator failed, using fallback: {e}")
            total_content = sum(len(m.response.content) for m in marks)
            dropped_content = sum(len(m.response.content) for m in dropped_marks)
            galois_loss = dropped_content / total_content if total_content > 0 else 0.0

            dropped_tags = list({tag for m in dropped_marks for tag in m.tags if tag})
            dropped_summaries = [
                m.response.content[:50] + "..."
                if len(m.response.content) > 50
                else m.response.content
                for m in dropped_marks[:3]
            ]

            honesty = CompressionHonesty(
                dropped_count=len(dropped_marks),
                dropped_tags=dropped_tags,
                dropped_summaries=dropped_summaries,
                galois_loss=galois_loss,
            )

        # Update crystal confidence based on Galois loss
        # Create new crystal with updated confidence (immutable pattern)
        crystal = Crystal.from_crystallization(
            insight=insight,
            significance=significance,
            principles=principles,
            source_marks=[MarkId(str(m.id)) for m in kept_marks],
            time_range=time_range,
            confidence=1.0 - galois_loss,  # Confidence inversely related to loss
            topics=topics,
            mood=mood,
        )

        # Store the crystal
        self._crystal_store.append(crystal)

        daily_crystal = DailyCrystal(
            crystal=crystal,
            honesty=honesty,
            level=level,
        )

        logger.info(
            f"Created {level.name} crystal: kept {len(kept_marks)}, "
            f"dropped {len(dropped_marks)}, loss {galois_loss:.1%}"
        )

        return daily_crystal

    def _generate_insight(self, marks: list[Mark], level: CrystalLevel) -> str:
        """Generate the core insight from marks."""
        # Extract unique content themes
        themes = []
        for mark in marks:
            content = mark.response.content
            # Take first sentence or first 100 chars
            first_sentence = content.split(".")[0][:100]
            themes.append(first_sentence)

        # WARMTH: Use conversational tone
        if level == CrystalLevel.DAY:
            prefix = "Today you worked on"
        elif level == CrystalLevel.WEEK:
            prefix = "This week centered on"
        else:
            prefix = "Key themes include"

        if len(themes) <= 2:
            return f"{prefix} {' and '.join(themes)}."
        else:
            return f"{prefix} {', '.join(themes[:2])}, and {len(themes) - 2} more."

    def _generate_significance(self, marks: list[Mark], level: CrystalLevel) -> str:
        """Generate why this matters."""
        # Look for eureka and veto marks
        eureka_count = sum(1 for m in marks if DailyTag.EUREKA.value in m.tags)
        veto_count = sum(1 for m in marks if DailyTag.VETO.value in m.tags)
        joy_count = sum(1 for m in marks if DailyTag.JOY.value in m.tags)

        # WARMTH: Warm, descriptive tone (not punitive)
        parts = []
        if eureka_count > 0:
            parts.append(f"{eureka_count} breakthrough{'s' if eureka_count > 1 else ''}")
        if veto_count > 0:
            parts.append(f"{veto_count} course correction{'s' if veto_count > 1 else ''}")
        if joy_count > 0:
            parts.append(f"{joy_count} moment{'s' if joy_count > 1 else ''} of delight")

        if not parts:
            return "A day of steady progress."

        return f"Notable: {', '.join(parts)}."

    def _extract_principles(self, marks: list[Mark]) -> list[str]:
        """Extract constitutional principles from marks."""
        principles = set()
        for mark in marks:
            if mark.constitutional:
                if mark.constitutional.dominant_principle:
                    principles.add(mark.constitutional.dominant_principle.lower())
        return list(principles) if principles else ["tasteful"]

    def _extract_topics(self, marks: list[Mark]) -> set[str]:
        """Extract topics from marks."""
        topics = set()
        for mark in marks:
            for tag in mark.tags:
                topics.add(tag)
        return topics


# =============================================================================
# Export: Shareable Artifacts
# =============================================================================


@dataclass
class DailyExport:
    """
    A shareable export of crystals and marks.

    The export uses a warm, personal tone suitable for sharing.
    """

    title: str
    date_range: tuple[date, date]
    crystals: list[DailyCrystal]
    key_marks: list[Mark]
    format: Literal["markdown", "json"] = "markdown"

    def to_markdown(self) -> str:
        """Generate markdown export with warm tone."""
        lines = [
            f"# {self.title}",
            "",
            f"*{self.date_range[0].isoformat()} to {self.date_range[1].isoformat()}*",
            "",
            WARMTH_PROMPTS["export_header"],
            "",
        ]

        # Crystals section
        if self.crystals:
            lines.append("## Crystallized Insights")
            lines.append("")
            for crystal in self.crystals:
                lines.append(f"### {crystal.level.name.title()} Crystal")
                lines.append("")
                lines.append(f"**Insight**: {crystal.insight}")
                lines.append("")
                lines.append(f"**Significance**: {crystal.significance}")
                lines.append("")
                lines.append(f"*{crystal.disclosure}*")
                lines.append("")

        # Key marks section
        if self.key_marks:
            lines.append("## Notable Moments")
            lines.append("")
            for mark in self.key_marks:
                tag_str = f"[{mark.tags[0]}]" if mark.tags else ""
                lines.append(f"- {tag_str} {mark.response.content}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Generated by kgents Daily Lab*")

        return "\n".join(lines)

    def to_json(self) -> str:
        """Generate JSON export."""
        return json.dumps(
            {
                "title": self.title,
                "date_range": [
                    self.date_range[0].isoformat(),
                    self.date_range[1].isoformat(),
                ],
                "crystals": [c.to_dict() for c in self.crystals],
                "key_marks": [m.to_dict() for m in self.key_marks],
            },
            indent=2,
        )

    def save(self, path: Path) -> None:
        """Save export to file."""
        if self.format == "markdown":
            path.write_text(self.to_markdown())
        else:
            path.write_text(self.to_json())
        logger.info(f"Saved export to {path}")


class DailyExporter:
    """
    Create shareable exports from daily lab data.

    WARMTH: "Here's a snapshot you can share."
    """

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        crystal_store: CrystalStore | None = None,
    ):
        # Use 'is not None' instead of 'or' because empty stores are falsy
        self._mark_store = mark_store if mark_store is not None else get_mark_store()
        self._crystal_store = crystal_store if crystal_store is not None else get_crystal_store()

    def export_day(
        self,
        target_date: date,
        include_crystal: bool = True,
        format: Literal["markdown", "json"] = "markdown",
    ) -> DailyExport:
        """Export a single day."""
        trail = Trail(self._mark_store)
        position = trail.for_date(target_date)

        # Filter to important marks
        important = trail.filter_by_importance(position)
        key_marks = important.marks[:5]  # Top 5 important marks

        # Get crystals if requested
        crystals: list[DailyCrystal] = []
        if include_crystal:
            crystallizer = DailyCrystallizer(self._mark_store, self._crystal_store)
            crystal = crystallizer.crystallize_day(target_date)
            if crystal:
                crystals.append(crystal)

        return DailyExport(
            title=f"Daily Review: {target_date.isoformat()}",
            date_range=(target_date, target_date),
            crystals=crystals,
            key_marks=key_marks,
            format=format,
        )

    def export_week(
        self,
        week_start: date | None = None,
        include_crystal: bool = True,
        format: Literal["markdown", "json"] = "markdown",
    ) -> DailyExport:
        """Export a week."""
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        week_end = week_start + timedelta(days=6)

        trail = Trail(self._mark_store)
        position = trail.for_week(week_start)

        # Filter to important marks
        important = trail.filter_by_importance(position)
        key_marks = important.marks[:10]  # Top 10 important marks for week

        # Get crystals if requested
        crystals: list[DailyCrystal] = []
        if include_crystal:
            crystallizer = DailyCrystallizer(self._mark_store, self._crystal_store)
            crystal = crystallizer.crystallize_week(week_start)
            if crystal:
                crystals.append(crystal)

        return DailyExport(
            title=f"Weekly Review: {week_start.isoformat()} to {week_end.isoformat()}",
            date_range=(week_start, week_end),
            crystals=crystals,
            key_marks=key_marks,
            format=format,
        )


# =============================================================================
# Daily Lab Service (High-Level API)
# =============================================================================


class DailyLab:
    """
    The main Daily Lab service.

    This is the primary entry point for the trail-to-crystal daily lab pilot.
    It combines mark capture, trail navigation, crystallization, and export
    into a cohesive, WARMTH-calibrated experience.

    Usage:
        lab = DailyLab()

        # Quick capture
        lab.capture.quick("Found a nice pattern in the code")

        # Tagged capture
        lab.capture.eureka("Realized the Galois connection works!")

        # Review today
        trail = lab.trail.for_today()
        while trail.current:
            print(trail.current.response.content)
            trail = lab.trail.navigate(trail, "next")

        # Create daily crystal
        crystal = lab.crystallize.day(date.today())
        print(crystal.insight)
        print(crystal.disclosure)

        # Export week
        export = lab.export.week()
        export.save(Path("week-review.md"))
    """

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        crystal_store: CrystalStore | None = None,
    ):
        # Use 'is not None' instead of 'or' because empty stores are falsy
        self._mark_store = mark_store if mark_store is not None else get_mark_store()
        self._crystal_store = crystal_store if crystal_store is not None else get_crystal_store()

        self.capture = DailyMarkCapture(self._mark_store)
        self.trail = Trail(self._mark_store)
        self.crystallize = DailyCrystallizer(self._mark_store, self._crystal_store)
        self.export = DailyExporter(self._mark_store, self._crystal_store)

    def today(self) -> TrailPosition:
        """Quick access to today's trail."""
        return self.trail.for_today()

    def review_prompt(self, position: TrailPosition) -> str:
        """Get a WARMTH-calibrated review prompt."""
        if position.total == 0:
            return WARMTH_PROMPTS["no_marks_found"]
        return WARMTH_PROMPTS["day_review"]

    def crystal_intro(self) -> str:
        """Get the crystallization intro prompt."""
        return WARMTH_PROMPTS["crystal_intro"]


# =============================================================================
# AGENTESE Contracts
# =============================================================================


@dataclass
class DailyLabManifestResponse:
    """Manifest response for witness.daily_lab."""

    today_mark_count: int
    today_crystal_count: int
    capture_prompt: str
    review_prompt: str
    status: str  # "ready", "has_marks", "crystallized"


@dataclass
class CaptureRequest:
    """Request for capturing a mark."""

    content: str
    tag: str | None = None  # eureka, gotcha, taste, friction, joy, veto
    reasoning: str | None = None


@dataclass
class CaptureResponse:
    """Response after capturing a mark."""

    mark_id: str
    content: str
    tag: str | None
    timestamp: str
    warmth_response: str


@dataclass
class TrailRequest:
    """Request for trail navigation."""

    date: str | None = None  # ISO date, defaults to today
    tags: list[str] | None = None  # Filter by tags
    important_only: bool = False


@dataclass
class TrailResponse:
    """Response with trail data."""

    total: int
    position: int
    marks: list[dict[str, Any]]
    review_prompt: str


@dataclass
class CrystallizeRequest:
    """Request for crystallization."""

    date: str | None = None  # ISO date, defaults to today
    force: bool = False  # Crystallize even with few marks


@dataclass
class CrystallizeResponse:
    """Response after crystallization."""

    crystal_id: str | None
    insight: str | None
    significance: str | None
    disclosure: str
    success: bool
    warmth_response: str


@dataclass
class ExportRequest:
    """Request for export."""

    date: str | None = None  # ISO date, defaults to today
    format: str = "markdown"  # markdown or json
    include_crystal: bool = True


@dataclass
class ExportResponse:
    """Response with export data."""

    content: str
    format: str
    warmth_response: str


# =============================================================================
# AGENTESE Node
# =============================================================================


@node(
    "witness.daily_lab",
    description="Daily Lab - Trail-to-Crystal journaling with WARMTH calibration",
    contracts={
        "manifest": ContractResponse(DailyLabManifestResponse),
        "capture": Contract(CaptureRequest, CaptureResponse),
        "trail": Contract(TrailRequest, TrailResponse),
        "crystallize": Contract(CrystallizeRequest, CrystallizeResponse),
        "export": Contract(ExportRequest, ExportResponse),
    },
    examples=[
        ("manifest", {}, "Get daily lab status"),
        ("capture", {"content": "Found a nice pattern"}, "Quick capture"),
        (
            "capture",
            {"content": "Breakthrough!", "tag": "eureka"},
            "Tagged capture",
        ),
        (
            "capture",
            {"content": "Design choice", "tag": "taste", "reasoning": "Aligns with joy-inducing"},
            "Capture with reasoning",
        ),
        ("trail", {}, "Get today's trail"),
        ("trail", {"important_only": True}, "Get important marks only"),
        ("crystallize", {}, "Create daily crystal"),
        ("export", {"format": "markdown"}, "Export as markdown"),
    ],
)
class DailyLabNode(BaseLogosNode):
    """
    AGENTESE node for Daily Lab Crown Jewel.

    Exposes the Daily Lab service through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    The Daily Lab provides a WARMTH-calibrated journaling experience:
    - Low-friction mark capture (FLOW joy)
    - Kind companion reviewing your day (WARMTH joy)
    - Honest compression with disclosure (Amendment G)

    Example:
        # Via AGENTESE gateway
        POST /agentese/witness/daily_lab/capture
        {"content": "Found a nice pattern", "tag": "eureka"}

        # Via Logos directly
        await logos.invoke("witness.daily_lab.trail", observer)

        # Via CLI
        kgents witness daily_lab trail
    """

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        crystal_store: CrystalStore | None = None,
    ) -> None:
        """
        Initialize DailyLabNode.

        Args:
            mark_store: The mark store (optional, uses global if not provided)
            crystal_store: The crystal store (optional, uses global if not provided)
        """
        self._lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

    @property
    def handle(self) -> str:
        return "witness.daily_lab"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Daily Lab is personal journaling, so access is broad:
        - developer/operator: Full access
        - architect/researcher: Full access (journaling is observational)
        - newcomer: Can view but not crystallize
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access
        if archetype_lower in (
            "developer",
            "operator",
            "admin",
            "system",
            "architect",
            "researcher",
        ):
            return (
                "manifest",
                "capture",
                "trail",
                "crystallize",
                "export",
            )

        # Newcomers: read-only
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return (
                "manifest",
                "trail",
            )

        # Guest: minimal
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest daily lab status to observer.

        AGENTESE: witness.daily_lab.manifest
        """
        # Get today's trail to count marks
        position = self._lab.today()
        today_marks = position.total

        # Check if we have a crystal for today
        # (crystals are stored in crystal_store)
        today_crystals = 0  # TODO: Query crystal store for today's crystals

        # Determine status
        if today_crystals > 0:
            status = "crystallized"
        elif today_marks > 0:
            status = "has_marks"
        else:
            status = "ready"

        return BasicRendering(
            summary=f"Daily Lab: {today_marks} marks today",
            content=f"Status: {status}. {self._lab.capture.prompt()}",
            metadata={
                "today_mark_count": today_marks,
                "today_crystal_count": today_crystals,
                "capture_prompt": self._lab.capture.prompt(),
                "review_prompt": self._lab.review_prompt(position),
                "status": status,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to Daily Lab methods."""
        if aspect == "capture":
            return await self._handle_capture(kwargs)
        elif aspect == "trail":
            return await self._handle_trail(kwargs)
        elif aspect == "crystallize":
            return await self._handle_crystallize(kwargs)
        elif aspect == "export":
            return await self._handle_export(kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_capture(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle capture aspect - capture a new mark."""
        content = kwargs.get("content", "")
        tag_str = kwargs.get("tag")
        reasoning = kwargs.get("reasoning")

        if not content:
            return {"error": "content required"}

        # Parse tag if provided
        tag: DailyTag | None = None
        if tag_str:
            try:
                tag = DailyTag(tag_str.lower())
            except ValueError:
                return {"error": f"Invalid tag: {tag_str}. Valid: {[t.value for t in DailyTag]}"}

        # Capture the mark
        if reasoning:
            dm = self._lab.capture.with_reasoning(content, reasoning, tag)
        elif tag:
            dm = self._lab.capture.tagged(content, tag)
        else:
            dm = self._lab.capture.quick(content)

        # Build warmth response
        if tag:
            warmth = WARMTH_RESPONSES["mark_captured_with_feeling"].format(tag=tag.value)
        else:
            warmth = WARMTH_RESPONSES["mark_captured"]

        return {
            "mark_id": str(dm.mark.id),
            "content": dm.content,
            "tag": dm.tag.value if dm.tag else None,
            "timestamp": dm.timestamp.isoformat(),
            "warmth_response": warmth,
        }

    async def _handle_trail(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle trail aspect - get trail of marks."""
        date_str = kwargs.get("date")
        tags_str = kwargs.get("tags")
        important_only = kwargs.get("important_only", False)

        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return {"error": f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD)"}

        # Get trail for date
        position = self._lab.trail.for_date(target_date)

        # Filter by importance if requested
        if important_only:
            position = self._lab.trail.filter_by_importance(position)

        # Build marks list
        marks_data = []
        for mark in position.marks:
            marks_data.append(
                {
                    "mark_id": str(mark.id),
                    "content": mark.response.content,
                    "tags": list(mark.tags),
                    "timestamp": mark.timestamp.isoformat(),
                }
            )

        return {
            "total": position.total,
            "position": position.position,
            "marks": marks_data,
            "review_prompt": self._lab.review_prompt(position),
        }

    async def _handle_crystallize(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle crystallize aspect - create a crystal from marks."""
        date_str = kwargs.get("date")
        force = kwargs.get("force", False)

        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return {"error": f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD)"}

        # Attempt crystallization
        crystal = self._lab.crystallize.crystallize_day(target_date)

        if crystal is None:
            return {
                "crystal_id": None,
                "insight": None,
                "significance": None,
                "disclosure": "Not enough marks to crystallize yet.",
                "success": False,
                "warmth_response": WARMTH_RESPONSES["nothing_to_compress"],
            }

        return {
            "crystal_id": str(crystal.crystal.id),
            "insight": crystal.insight,
            "significance": crystal.significance,
            "disclosure": crystal.disclosure,
            "success": True,
            "warmth_response": WARMTH_RESPONSES["crystal_created"],
        }

    async def _handle_export(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle export aspect - export the day's work."""
        date_str = kwargs.get("date")
        format_str = kwargs.get("format", "markdown")
        include_crystal = kwargs.get("include_crystal", True)

        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return {"error": f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD)"}

        # Validate format
        if format_str not in ("markdown", "json"):
            return {"error": f"Invalid format: {format_str}. Valid: markdown, json"}

        # Create export
        export = self._lab.export.export_day(
            target_date,
            include_crystal=include_crystal,
            format=format_str,
        )

        # Get content based on format
        if format_str == "markdown":
            content = export.to_markdown()
        else:
            content = export.to_json()

        return {
            "content": content,
            "format": format_str,
            "warmth_response": WARMTH_RESPONSES["export_ready"],
        }


# Factory function for the node
_daily_lab_node: DailyLabNode | None = None


def get_daily_lab_node() -> DailyLabNode:
    """Get the singleton DailyLabNode instance."""
    global _daily_lab_node
    if _daily_lab_node is None:
        _daily_lab_node = DailyLabNode()
    return _daily_lab_node


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Tags
    "DailyTag",
    # Mark capture
    "DailyMark",
    "DailyMarkCapture",
    # Trail navigation
    "Trail",
    "TrailPosition",
    # Crystal compression
    "CompressionHonesty",
    "DailyCrystal",
    "DailyCrystallizer",
    # Export
    "DailyExport",
    "DailyExporter",
    # Service
    "DailyLab",
    # AGENTESE Node
    "DailyLabNode",
    "get_daily_lab_node",
    # Contracts
    "DailyLabManifestResponse",
    "CaptureRequest",
    "CaptureResponse",
    "TrailRequest",
    "TrailResponse",
    "CrystallizeRequest",
    "CrystallizeResponse",
    "ExportRequest",
    "ExportResponse",
    # Prompts
    "WARMTH_PROMPTS",
    "WARMTH_RESPONSES",
]
