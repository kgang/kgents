"""
Crystallizer: LLM-Powered Semantic Compression.

The Crystallizer transforms marks and crystals into higher-level insights
using K-gent's LLM capabilities. This is LLM-first crystallization:
rich semantic compression from the start.

The Crystallization Process:
1. Format source material (marks or crystals) for LLM context
2. Invoke K-gent with structured crystallization prompt
3. Parse JSON response into Crystal fields
4. Derive mood vector from source material
5. Compute confidence from LLM response

Philosophy:
    "Crystallization is not summarization. It's semantic compression that
    preserves causal structure while revealing emergent patterns."

    The LLM doesn't just condense—it interprets, connects, and extracts
    the significance that a simple summary would miss.

Integration:
    Uses K-gent Soul for LLM access. Falls back to template extraction
    if LLM is unavailable (graceful degradation).

See: spec/protocols/witness-crystallization.md
See: agents/k/soul.py
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol

from .crystal import Crystal, CrystalId, CrystalLevel, MoodVector
from .mark import Mark, MarkId
from .trace_store import MarkStore

if TYPE_CHECKING:
    from agents.k.soul import BudgetTier, KgentSoul

logger = logging.getLogger("kgents.witness.crystallizer")


# =============================================================================
# Crystallization Prompts
# =============================================================================

CRYSTALLIZATION_PROMPT_MARKS = """You are crystallizing witness marks into dense, actionable insight.

MARKS (chronological):
{marks_formatted}

TIME SPAN: {time_span}
MARK COUNT: {mark_count}

CRYSTALLIZE by answering these questions:

1. WHAT HAPPENED? (concrete actions, not abstractions - what actually got done?)
2. WHY DOES IT MATTER? (significance to the project/person - what changed?)
3. WHAT EMERGED? (principles, patterns, learnings that weren't explicit before)

Be CONCRETE. Be DENSE. Preserve CAUSALITY.

Respond ONLY with valid JSON (no markdown code fences):
{{
  "insight": "1-3 sentences capturing the essence of what happened",
  "significance": "1-2 sentences on why this matters going forward",
  "principles": ["principle1", "principle2"],
  "topics": ["topic1", "topic2", "topic3"],
  "confidence": 0.8
}}

Guidelines:
- insight: What actually happened, in specific terms
- significance: The "so what" - how this affects future work
- principles: Kgents principles that emerged (tasteful, curated, ethical, joy-inducing, composable, heterarchical, generative)
- topics: Key concepts/areas touched (for retrieval)
- confidence: Your confidence in this crystallization (0.0-1.0)
"""

CRYSTALLIZATION_PROMPT_CRYSTALS = """You are crystallizing session insights into a higher-level {level_name} crystal.

SOURCE CRYSTALS:
{crystals_formatted}

CRYSTAL COUNT: {crystal_count}
COMBINED TIME SPAN: {time_span}

SYNTHESIZE these crystals into a SINGLE higher-level insight:

1. What THEME connects these sessions?
2. What PROGRESS was made across this period?
3. What PATTERNS emerged that weren't visible in individual sessions?

Respond ONLY with valid JSON (no markdown code fences):
{{
  "insight": "1-3 sentences capturing the essence of this period",
  "significance": "1-2 sentences on why this matters going forward",
  "principles": ["principle1", "principle2"],
  "topics": ["topic1", "topic2", "topic3"],
  "confidence": 0.8
}}

Guidelines:
- insight: The meta-pattern across sessions
- significance: What this period achieved or changed
- principles: Dominant principles that guided the work
- topics: Key themes (for retrieval)
- confidence: Your confidence in this synthesis (0.0-1.0)
"""


# =============================================================================
# Soul Protocol (for dependency injection)
# =============================================================================


class SoulProtocol(Protocol):
    """Protocol for Soul-like objects (enables testing with mocks)."""

    @property
    def has_llm(self) -> bool:
        """Whether LLM is available."""
        ...

    async def dialogue(
        self,
        message: str,
        mode: Any = None,
        budget: Any = None,
    ) -> Any:
        """Invoke dialogue with K-gent."""
        ...


# =============================================================================
# Crystallization Result
# =============================================================================


@dataclass
class CrystallizationResult:
    """Result of a crystallization operation."""

    insight: str
    significance: str
    principles: list[str]
    topics: list[str]
    confidence: float
    raw_response: str = ""
    used_llm: bool = False


# =============================================================================
# Crystallizer
# =============================================================================


class Crystallizer:
    """
    LLM-powered semantic compression for witness memory.

    The Crystallizer transforms marks/crystals into higher-level crystals
    using K-gent's LLM capabilities. It is LLM-first but degrades gracefully
    to template extraction when LLM is unavailable.

    Example:
        >>> from agents.k.soul import KgentSoul
        >>> soul = KgentSoul()
        >>> crystallizer = Crystallizer(soul)
        >>> crystal = await crystallizer.crystallize_marks(marks, session_id="abc")
        >>> print(crystal.insight)
        "Completed extinction audit, removed 52K lines of stale code"

    Integration:
        Uses K-gent Soul for LLM access. The Soul handles:
        - LLM client management
        - Budget tiers (DIALOGUE for crystallization)
        - Graceful degradation to templates
    """

    def __init__(
        self,
        soul: SoulProtocol | None = None,
        mark_store: MarkStore | None = None,
    ) -> None:
        """
        Initialize the Crystallizer.

        Args:
            soul: K-gent Soul for LLM access. If None, will use template fallback.
            mark_store: MarkStore for sealing marks. If None, marks won't be sealed.
        """
        self._soul = soul
        self._mark_store = mark_store

    def set_soul(self, soul: SoulProtocol) -> None:
        """Set the Soul for LLM access (for late binding/testing)."""
        self._soul = soul

    def set_mark_store(self, mark_store: MarkStore) -> None:
        """Set the MarkStore for sealing marks (for late binding/testing)."""
        self._mark_store = mark_store

    @property
    def has_llm(self) -> bool:
        """Check if LLM is available."""
        return self._soul is not None and self._soul.has_llm

    # =========================================================================
    # Core Crystallization Methods
    # =========================================================================

    async def crystallize_marks(
        self,
        marks: list[Mark],
        session_id: str = "",
        seal_marks: bool = True,
    ) -> Crystal:
        """
        Crystallize marks into a level-0 (SESSION) crystal.

        This is the primary entry point for crystallization. It:
        1. Formats marks for LLM context
        2. Invokes K-gent with crystallization prompt
        3. Parses response and creates Crystal
        4. Seals source marks (if mark_store is available and seal_marks=True)

        Args:
            marks: List of marks to crystallize (should be from same session)
            session_id: Optional session identifier
            seal_marks: Whether to seal marks after crystallization (default True)

        Returns:
            A level-0 Crystal containing the crystallized insight

        Raises:
            ValueError: If marks list is empty
        """
        if not marks:
            raise ValueError("Cannot crystallize empty marks list")

        # Sort by timestamp
        marks = sorted(marks, key=lambda m: m.timestamp)

        # Extract time range
        time_range = (marks[0].timestamp, marks[-1].timestamp)

        # Attempt LLM crystallization
        result = await self._crystallize_with_llm_marks(marks, time_range)

        # Derive mood from marks
        mood = MoodVector.from_marks(marks)

        # Create crystal
        crystal = Crystal.from_crystallization(
            insight=result.insight,
            significance=result.significance,
            principles=result.principles,
            source_marks=[m.id for m in marks],
            time_range=time_range,
            confidence=result.confidence,
            topics=set(result.topics),
            mood=mood,
            session_id=session_id,
        )

        # Seal marks if mark_store is available
        if seal_marks and self._mark_store is not None:
            mark_ids = [str(m.id) for m in marks]
            sealed_count = self._mark_store.seal_marks(mark_ids, str(crystal.id))
            logger.info(f"Sealed {sealed_count} marks with crystal {crystal.id}")

        return crystal

    async def crystallize_crystals(
        self,
        crystals: list[Crystal],
        level: CrystalLevel,
    ) -> Crystal:
        """
        Crystallize crystals into a higher-level crystal.

        Used for DAY, WEEK, and EPOCH crystals.

        Args:
            crystals: List of crystals to crystallize (should be from level N-1)
            level: Target level (DAY, WEEK, or EPOCH)

        Returns:
            A higher-level Crystal containing the synthesized insight

        Raises:
            ValueError: If crystals list is empty or level is SESSION
        """
        if not crystals:
            raise ValueError("Cannot crystallize empty crystals list")

        if level == CrystalLevel.SESSION:
            raise ValueError("Use crystallize_marks for SESSION level")

        # Validate source levels
        expected_source_level = CrystalLevel(level.value - 1)
        for crystal in crystals:
            if crystal.level != expected_source_level:
                raise ValueError(
                    f"Expected level {expected_source_level.name} crystals, "
                    f"got level {crystal.level.name}"
                )

        # Sort by time
        crystals = sorted(crystals, key=lambda c: c.crystallized_at)

        # Attempt LLM crystallization
        result = await self._crystallize_with_llm_crystals(crystals, level)

        # Aggregate mood (weighted average by source count)
        total_sources = sum(c.source_count for c in crystals)
        if total_sources > 0:
            mood = MoodVector(
                warmth=sum(c.mood.warmth * c.source_count for c in crystals) / total_sources,
                weight=sum(c.mood.weight * c.source_count for c in crystals) / total_sources,
                tempo=sum(c.mood.tempo * c.source_count for c in crystals) / total_sources,
                texture=sum(c.mood.texture * c.source_count for c in crystals) / total_sources,
                brightness=sum(c.mood.brightness * c.source_count for c in crystals)
                / total_sources,
                saturation=sum(c.mood.saturation * c.source_count for c in crystals)
                / total_sources,
                complexity=sum(c.mood.complexity * c.source_count for c in crystals)
                / total_sources,
            )
        else:
            mood = MoodVector.neutral()

        # Aggregate topics
        all_topics: set[str] = set()
        for crystal in crystals:
            all_topics.update(crystal.topics)
        all_topics.update(result.topics)

        return Crystal.from_crystals(
            insight=result.insight,
            significance=result.significance,
            principles=result.principles,
            source_crystals=[c.id for c in crystals],
            level=level,
            confidence=result.confidence,
            topics=all_topics,
            mood=mood,
        )

    # =========================================================================
    # LLM Integration
    # =========================================================================

    async def _crystallize_with_llm_marks(
        self,
        marks: list[Mark],
        time_range: tuple[datetime, datetime],
    ) -> CrystallizationResult:
        """Use LLM to crystallize marks."""
        if not self.has_llm:
            logger.info("No LLM available, using template extraction")
            return self._template_crystallize_marks(marks)

        # Format marks for prompt
        marks_formatted = self._format_marks(marks)
        time_span = self._format_time_span(time_range)

        prompt = CRYSTALLIZATION_PROMPT_MARKS.format(
            marks_formatted=marks_formatted,
            time_span=time_span,
            mark_count=len(marks),
        )

        try:
            # Import here to avoid circular imports
            from agents.k.persona import DialogueMode
            from agents.k.soul import BudgetTier

            # Soul is guaranteed to exist here (checked in has_llm)
            assert self._soul is not None
            response = await self._soul.dialogue(
                message=prompt,
                mode=DialogueMode.REFLECT,
                budget=BudgetTier.DIALOGUE,
            )

            result = self._parse_llm_response(response.response)

            # If parsing/validation failed, fall back to template
            if result is None:
                logger.warning("LLM response failed validation, falling back to template")
                return self._template_crystallize_marks(marks)

            result.used_llm = True
            result.raw_response = response.response
            return result

        except Exception as e:
            logger.warning(f"LLM crystallization failed: {e}, falling back to template")
            return self._template_crystallize_marks(marks)

    async def _crystallize_with_llm_crystals(
        self,
        crystals: list[Crystal],
        level: CrystalLevel,
    ) -> CrystallizationResult:
        """Use LLM to crystallize crystals."""
        if not self.has_llm:
            logger.info("No LLM available, using template extraction")
            return self._template_crystallize_crystals(crystals, level)

        # Format crystals for prompt
        crystals_formatted = self._format_crystals(crystals)

        # Compute combined time span
        all_times: list[datetime] = []
        for c in crystals:
            if c.time_range:
                all_times.extend(c.time_range)
        if all_times:
            time_span = self._format_time_span((min(all_times), max(all_times)))
        else:
            time_span = "unknown"

        prompt = CRYSTALLIZATION_PROMPT_CRYSTALS.format(
            crystals_formatted=crystals_formatted,
            crystal_count=len(crystals),
            time_span=time_span,
            level_name=level.name_display,
        )

        try:
            from agents.k.persona import DialogueMode
            from agents.k.soul import BudgetTier

            # Soul is guaranteed to exist here (checked in has_llm)
            assert self._soul is not None
            response = await self._soul.dialogue(
                message=prompt,
                mode=DialogueMode.REFLECT,
                budget=BudgetTier.DIALOGUE,
            )

            result = self._parse_llm_response(response.response)

            # If parsing/validation failed, fall back to template
            if result is None:
                logger.warning("LLM response failed validation, falling back to template")
                return self._template_crystallize_crystals(crystals, level)

            result.used_llm = True
            result.raw_response = response.response
            return result

        except Exception as e:
            logger.warning(f"LLM crystallization failed: {e}, falling back to template")
            return self._template_crystallize_crystals(crystals, level)

    # =========================================================================
    # Template Fallback (No LLM)
    # =========================================================================

    def _template_crystallize_marks(self, marks: list[Mark]) -> CrystallizationResult:
        """Template-based crystallization when LLM unavailable."""
        # Extract key information from marks
        actions = [m.response.content for m in marks[:10]]  # First 10 actions
        tags: set[str] = set()
        for m in marks:
            tags.update(m.tags)

        # Generate template insight
        if len(marks) == 1:
            insight = actions[0] if actions else "Single action recorded"
        else:
            insight = f"{len(marks)} actions recorded"
            if actions:
                insight += f": {actions[0][:50]}..."

        significance = f"Captured {len(marks)} marks with {len(tags)} unique tags"

        # Extract principles from tags
        kgent_principles = [
            "tasteful",
            "curated",
            "ethical",
            "joy-inducing",
            "composable",
            "heterarchical",
            "generative",
        ]
        principles = [t for t in tags if t.lower() in kgent_principles]

        # Use tags as topics
        topics = list(tags)[:5]

        return CrystallizationResult(
            insight=insight,
            significance=significance,
            principles=principles,
            topics=topics,
            confidence=0.5,  # Lower confidence for template
            used_llm=False,
        )

    def _template_crystallize_crystals(
        self,
        crystals: list[Crystal],
        level: CrystalLevel,
    ) -> CrystallizationResult:
        """Template-based crystallization for higher levels."""
        # Aggregate insights
        insights = [c.insight for c in crystals[:5]]
        insight = f"{len(crystals)} {level.name_display.lower()} sessions synthesized"

        # Aggregate significance
        significance = f"Covering {sum(c.source_count for c in crystals)} sources"

        # Aggregate principles (most common)
        all_principles: list[str] = []
        for c in crystals:
            all_principles.extend(c.principles)
        principle_counts: dict[str, int] = {}
        for p in all_principles:
            principle_counts[p] = principle_counts.get(p, 0) + 1
        principles = sorted(principle_counts.keys(), key=lambda p: -principle_counts[p])[:3]

        # Aggregate topics
        all_topics: set[str] = set()
        for c in crystals:
            all_topics.update(c.topics)
        topics = list(all_topics)[:5]

        return CrystallizationResult(
            insight=insight,
            significance=significance,
            principles=principles,
            topics=topics,
            confidence=0.4,  # Lower confidence for template
            used_llm=False,
        )

    # =========================================================================
    # Formatting Helpers
    # =========================================================================

    def _format_marks(self, marks: list[Mark]) -> str:
        """Format marks for LLM prompt."""
        lines = []
        for i, mark in enumerate(marks[:30], 1):  # Limit to 30 marks
            timestamp = mark.timestamp.strftime("%H:%M")
            content = mark.response.content[:200]  # Truncate long content
            tags = ", ".join(mark.tags) if mark.tags else ""
            # Get reasoning from metadata (Mark doesn't have direct reasoning field)
            reasoning_text = mark.metadata.get("reasoning", "")
            reasoning = f" [{reasoning_text}]" if reasoning_text else ""

            line = f"{i}. [{timestamp}] {content}"
            if tags:
                line += f" (tags: {tags})"
            if reasoning:
                line += reasoning
            lines.append(line)

        return "\n".join(lines)

    def _format_crystals(self, crystals: list[Crystal]) -> str:
        """Format crystals for LLM prompt."""
        lines = []
        for i, crystal in enumerate(crystals[:10], 1):  # Limit to 10 crystals
            date = crystal.crystallized_at.strftime("%Y-%m-%d")
            insight = crystal.insight[:200]
            significance = crystal.significance[:100] if crystal.significance else ""
            confidence = crystal.confidence

            line = f"{i}. [{date}] {insight}"
            if significance:
                line += f"\n   Significance: {significance}"
            line += f"\n   (confidence: {confidence:.2f}, sources: {crystal.source_count})"
            lines.append(line)

        return "\n\n".join(lines)

    def _format_time_span(self, time_range: tuple[datetime, datetime]) -> str:
        """Format time range for display."""
        start, end = time_range
        duration = end - start

        if duration.days > 0:
            return f"{duration.days}d {duration.seconds // 3600}h"
        elif duration.seconds >= 3600:
            return f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
        else:
            return f"{duration.seconds // 60}m"

    def _validate_result(self, result: CrystallizationResult) -> bool:
        """
        Validate a crystallization result to prevent gibberish from being stored.

        Returns:
            True if the result is valid, False if it contains gibberish.
        """
        insight = result.insight.strip()

        # Reject if insight is too short
        if len(insight) < 20:
            logger.warning(f"Rejected insight (too short): {insight[:50]}")
            return False

        # Reject if insight starts with JSON syntax
        if insight.startswith("{") or insight.startswith("["):
            logger.warning(f"Rejected insight (JSON fragment): {insight[:50]}")
            return False

        # Reject if insight contains error patterns
        error_patterns = ["error:", "exception:", "traceback:", "system:", "```json"]
        for pattern in error_patterns:
            if pattern in insight.lower():
                logger.warning(f"Rejected insight (error pattern '{pattern}'): {insight[:50]}")
                return False

        return True

    def _parse_llm_response(self, response: str) -> CrystallizationResult | None:
        """
        Parse LLM JSON response into CrystallizationResult.

        Returns:
            CrystallizationResult if valid, None if parsing or validation fails.
        """
        # Clean response - remove markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # Remove first line (```json or ```)
            lines = cleaned.split("\n")
            lines = lines[1:]  # Remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove closing fence
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
            result = CrystallizationResult(
                insight=data.get("insight", ""),
                significance=data.get("significance", ""),
                principles=data.get("principles", []),
                topics=data.get("topics", []),
                confidence=float(data.get("confidence", 0.8)),
            )

            # Validate the parsed result
            if not self._validate_result(result):
                logger.warning("JSON parsed successfully but validation failed")
                return None

            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")
            # Attempt to extract fields with regex as fallback
            return self._regex_extract(response)

    def _regex_extract(self, response: str) -> CrystallizationResult | None:
        """
        Fallback: extract fields with regex if JSON parsing fails.

        Returns:
            CrystallizationResult if valid fields were extracted, None otherwise.
        """
        insight = ""
        significance = ""
        principles: list[str] = []
        topics: list[str] = []
        confidence = 0.6

        # Try to find insight
        insight_match = re.search(r'"insight":\s*"([^"]+)"', response)
        if insight_match:
            insight = insight_match.group(1)

        # Try to find significance
        sig_match = re.search(r'"significance":\s*"([^"]+)"', response)
        if sig_match:
            significance = sig_match.group(1)

        # Try to find confidence
        conf_match = re.search(r'"confidence":\s*([\d.]+)', response)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
            except ValueError:
                pass

        # If we got something, validate it
        if insight:
            result = CrystallizationResult(
                insight=insight,
                significance=significance,
                principles=principles,
                topics=topics,
                confidence=confidence * 0.7,  # Penalize regex extraction
            )

            if self._validate_result(result):
                return result
            else:
                logger.warning("Regex extraction succeeded but validation failed")
                return None

        # No valid extraction possible
        logger.warning("Regex extraction found no valid insight field")
        return None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Crystallizer",
    "CrystallizationResult",
    "CRYSTALLIZATION_PROMPT_MARKS",
    "CRYSTALLIZATION_PROMPT_CRYSTALS",
]
