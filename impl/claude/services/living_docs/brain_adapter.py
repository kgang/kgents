"""
HydrationBrainAdapter: Wire Brain semantic search to Living Docs hydration.

Checkpoint 0.2 of Metabolic Development Protocol.

User Journey:
    kg docs hydrate "finish verification integration"
        ↓
    Brain vectors find semantically similar gotchas
        ↓
    ASHC prior evidence for similar work surfaces
        ↓
    Context compiled with semantic depth

The adapter bridges keyword-based hydration with Brain's semantic search,
enabling "what did I learn about X?" style queries.

Teaching:
    gotcha: Brain requires async session; Hydrator is sync.
            Use asyncio.run() or async API for integration.
            (Evidence: test_brain_adapter.py::TestSemanticTeaching::test_returns_teaching_from_brain_results)

    gotcha: Brain may return empty if no crystals exist.
            Fall back to keyword matching gracefully.
            (Evidence: test_brain_adapter.py::TestSemanticTeaching::test_returns_empty_without_brain)

AGENTESE: concept.docs.hydrate (enhanced with semantic matching)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from .types import TeachingMoment

if TYPE_CHECKING:
    from services.brain.persistence import BrainPersistence, SearchResult


@dataclass
class ScoredTeachingResult:
    """
    A teaching result with similarity score for semantic ranking.

    Wraps a TeachingMoment with additional metadata for semantic search results.
    Not frozen so we can add attributes dynamically if needed.
    """

    moment: TeachingMoment
    symbol: str
    module: str
    source_path: str | None = None
    score: float = 0.0  # Similarity score from semantic search


logger = logging.getLogger(__name__)


# =============================================================================
# ASHC Evidence Integration (Stub for Phase 2)
# =============================================================================


@dataclass
class ASHCEvidence:
    """
    Prior evidence from ASHC for related work.

    This will be populated in Phase 2 (ASHC Continuous Mode).
    For now, it's a stub that demonstrates the integration point.
    """

    task_pattern: str  # e.g., "verification integration"
    run_count: int
    pass_rate: float
    diversity_score: float
    last_run: str  # ISO date
    causal_insights: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_pattern": self.task_pattern,
            "run_count": self.run_count,
            "pass_rate": self.pass_rate,
            "diversity_score": self.diversity_score,
            "last_run": self.last_run,
            "causal_insights": self.causal_insights,
        }


# =============================================================================
# Brain Adapter
# =============================================================================


class HydrationBrainAdapter:
    """
    Adapter that connects Living Docs hydration to Brain semantic search.

    The core insight: Brain crystals ARE teaching moments captured over time.
    When Kent captures something with tags like "gotcha", "lesson", or
    "verification", Brain can surface semantically related crystals.

    This enables:
    - Semantic similarity instead of just keyword matching
    - Historical learning retrieval ("what did I learn about X?")
    - Cross-session knowledge accumulation

    Usage:
        adapter = HydrationBrainAdapter(brain_persistence)

        # Get semantically similar teaching moments
        moments = await adapter.find_semantic_teaching("verification tests")

        # Get prior evidence from ASHC (Phase 2)
        evidence = await adapter.find_prior_evidence("verification")
    """

    def __init__(
        self,
        brain: "BrainPersistence | None" = None,
    ):
        """
        Initialize adapter.

        Args:
            brain: Optional BrainPersistence instance
        """
        self.brain = brain

    @property
    def is_available(self) -> bool:
        """Check if Brain integration is available."""
        return self.brain is not None

    # =========================================================================
    # Semantic Teaching Moments
    # =========================================================================

    async def find_semantic_teaching(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.3,
    ) -> list[ScoredTeachingResult]:
        """
        Find teaching moments using Brain's semantic search.

        Searches Brain crystals tagged with teaching-related terms
        and converts matches to TeachingResult format.

        Args:
            query: Natural language query
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of TeachingResult from semantic matches
        """
        if not self.brain:
            logger.debug("Brain not available for semantic teaching search")
            return []

        try:
            # Search Brain for teaching-related crystals
            # Tags we care about: gotcha, lesson, learning, teaching, mistake
            results = await self.brain.search(
                query=query,
                limit=limit * 2,  # Get more, then filter
                tags=None,  # Search all, filter later
            )

            teaching_results: list[ScoredTeachingResult] = []
            for result in results:
                # Filter by similarity threshold
                if result.similarity < min_similarity:
                    continue

                # Convert Brain SearchResult to ScoredTeachingResult
                teaching = self._convert_to_teaching(result)
                if teaching:
                    teaching_results.append(teaching)

                if len(teaching_results) >= limit:
                    break

            logger.debug(f"Found {len(teaching_results)} semantic teaching moments")
            return teaching_results

        except Exception as e:
            logger.warning(f"Semantic teaching search failed: {e}")
            return []

    def _convert_to_teaching(
        self,
        result: "SearchResult",
    ) -> ScoredTeachingResult | None:
        """
        Convert a Brain SearchResult to a ScoredTeachingResult.

        Brain crystals may contain teaching content in various formats.
        We try to extract the essence and convert to TeachingMoment.
        """
        content = result.content
        summary = result.summary

        # Try to extract teaching insight from content
        insight = self._extract_insight(content)
        if not insight:
            # Use summary as fallback
            insight = summary

        # Determine severity based on keywords
        severity = self._infer_severity(content)

        # Create teaching moment
        moment = TeachingMoment(
            insight=insight,
            severity=severity,
            evidence=f"brain:{result.crystal_id}",
        )

        # Create scored result with similarity
        return ScoredTeachingResult(
            moment=moment,
            symbol=f"brain.{result.crystal_id[:8]}",
            module="brain_crystal",
            source_path=f"brain:{result.crystal_id}",
            score=result.similarity,
        )

    def _extract_insight(self, content: str) -> str | None:
        """
        Extract the teaching insight from crystal content.

        Looks for patterns like:
        - "gotcha: ..."
        - "lesson: ..."
        - "learned: ..."
        - Lines starting with "- " that contain teaching
        """
        import re

        # Try to find explicit teaching patterns
        patterns = [
            r"(?:gotcha|lesson|learned|insight|teaching|warning|critical):\s*(.+)",
            r"^[-•]\s*(.+)$",  # Bullet points often contain insights
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()

        # Fallback: first non-empty line
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                return line if len(line) <= 200 else line[:200] + "..."

        return None

    def _infer_severity(self, content: str) -> Literal["info", "warning", "critical"]:
        """Infer severity from content keywords."""
        content_lower = content.lower()

        critical_keywords = ["critical", "never", "must not", "fatal", "break", "crash"]
        warning_keywords = ["warning", "careful", "avoid", "don't", "gotcha"]

        if any(kw in content_lower for kw in critical_keywords):
            return "critical"
        if any(kw in content_lower for kw in warning_keywords):
            return "warning"
        return "info"

    # =========================================================================
    # ASHC Evidence (Phase 2 Implementation)
    # =========================================================================

    async def find_prior_evidence(
        self,
        task_pattern: str,
        limit: int = 3,
    ) -> list[ASHCEvidence]:
        """
        Find prior ASHC evidence for similar work.

        Uses BackgroundEvidencing from metabolism to find accumulated
        evidence from previous verification runs.

        Args:
            task_pattern: Pattern to search for
            limit: Maximum evidence entries

        Returns:
            List of ASHCEvidence from background accumulation
        """
        try:
            from services.metabolism.evidencing import get_background_evidencing

            accumulator = get_background_evidencing()
            matches = accumulator.find_matching_evidence(task_pattern, limit=limit)

            results: list[ASHCEvidence] = []
            for stored in matches:
                # Get causal insights for this pattern
                insights = accumulator.get_insights(task_pattern)
                insight_strs = [
                    f"{i.nudge_pattern}: {'+' if i.outcome_delta > 0 else ''}{i.outcome_delta:.1%}"
                    for i in insights[:3]  # Top 3 insights
                ]

                evidence = ASHCEvidence(
                    task_pattern=stored.task_pattern,
                    run_count=stored.run_count,
                    pass_rate=stored.pass_rate,
                    diversity_score=stored.diversity_score,
                    last_run=stored.last_run_at.isoformat() if stored.last_run_at else "",
                    causal_insights=insight_strs,
                )
                results.append(evidence)

            logger.debug(f"Found {len(results)} prior evidence entries for: {task_pattern}")
            return results

        except ImportError:
            logger.debug("BackgroundEvidencing not available")
            return []
        except Exception as e:
            logger.warning(f"ASHC evidence search failed: {e}")
            return []

    # =========================================================================
    # Combined Semantic Hydration
    # =========================================================================

    async def semantic_hydrate(
        self,
        task: str,
        teaching_limit: int = 10,
        evidence_limit: int = 3,
    ) -> dict[str, Any]:
        """
        Get combined semantic context for a task.

        This is the main entry point for semantic hydration,
        combining Brain teaching moments with ASHC evidence.

        Args:
            task: The task description
            teaching_limit: Max teaching moments to return
            evidence_limit: Max ASHC evidence entries

        Returns:
            Dict with:
            - semantic_teaching: Teaching moments from Brain
            - prior_evidence: Evidence from ASHC
            - brain_available: Whether Brain was used
        """
        result = {
            "semantic_teaching": [],
            "prior_evidence": [],
            "brain_available": self.is_available,
        }

        if self.is_available:
            # Get semantic teaching moments
            teaching = await self.find_semantic_teaching(task, limit=teaching_limit)
            result["semantic_teaching"] = teaching

            # Get prior evidence (Phase 2)
            evidence = await self.find_prior_evidence(task, limit=evidence_limit)
            result["prior_evidence"] = evidence

        return result


# =============================================================================
# Factory
# =============================================================================


_adapter: HydrationBrainAdapter | None = None


def get_hydration_brain_adapter() -> HydrationBrainAdapter:
    """Get or create the global HydrationBrainAdapter."""
    global _adapter
    if _adapter is None:
        # Create without Brain for now - will be wired at runtime
        _adapter = HydrationBrainAdapter()
    return _adapter


def set_hydration_brain_adapter(adapter: HydrationBrainAdapter) -> None:
    """Set the global HydrationBrainAdapter (for DI/testing)."""
    global _adapter
    _adapter = adapter


def reset_hydration_brain_adapter() -> None:
    """Reset the global adapter."""
    global _adapter
    _adapter = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "ASHCEvidence",
    "ScoredTeachingResult",
    # Adapter
    "HydrationBrainAdapter",
    "get_hydration_brain_adapter",
    "set_hydration_brain_adapter",
    "reset_hydration_brain_adapter",
]
