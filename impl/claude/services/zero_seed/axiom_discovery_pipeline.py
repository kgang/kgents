"""
Axiom Discovery Pipeline for Zero Seed Personal Governance.

Discovers personal axioms - the L<0.05 fixed points Kent never violates.
This is the core insight from zero-seed-personal-governance-lab:

    "Kent discovers his personal axioms. The system shows him:
     'You've made 147 decisions this month. Here are the 3 principles
      you never violated — your L0 axioms.'"

Pipeline stages:
    1. SURFACE: Query decisions from past N days via MarkStore
    2. COMPUTE: Calculate Galois loss for each pattern with caching
    3. IDENTIFY: Find fixed points where L < 0.05
    4. CLUSTER: Group semantically similar low-loss patterns
    5. VERIFY: Check stability under repeated R-C cycles
    6. DETECT: Find contradictions via super-additive loss
    7. PRESENT: Top-K axiom candidates with evidence

Key formulas:
    - Axiom: L(P) < 0.05 (content that survives restructure-reconstitute)
    - Fixed point: R^∞(P) = Fix(P) where R is restructure
    - Contradiction: L(A∪B) > L(A) + L(B) + τ signals conflict

Philosophy:
    "Axioms are not stipulated but discovered.
     They are the fixed points of your decision landscape.
     The proof IS the decision. The mark IS the witness."

See: spec/protocols/zero-seed.md
See: zero-seed-personal-governance-lab pilot
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from .axiom_discovery import (
    AXIOM_THRESHOLD,
    AxiomDiscoveryService,
    DiscoveredAxiom,
    extract_value_phrases,
)
from .galois import (
    FIXED_POINT_THRESHOLD,
    STABILITY_THRESHOLD,
    FixedPointResult,
    detect_fixed_point,
)
from .galois.galois_loss import (
    CONTRADICTION_TOLERANCE,
    GaloisLossComputer,
    LossCache,
    detect_contradiction,
)

if TYPE_CHECKING:
    from services.witness import Mark, MarkStore

logger = logging.getLogger("kgents.zero_seed.axiom_discovery_pipeline")


# =============================================================================
# Constants
# =============================================================================

# Default time window for decision analysis
DEFAULT_TIME_WINDOW_DAYS: int = 30

# Minimum decisions needed for pattern detection
MIN_DECISIONS_FOR_PATTERN: int = 5

# Maximum candidates to analyze (performance bound)
MAX_ANALYSIS_CANDIDATES: int = 20

# Contradiction detection threshold (τ)
CONTRADICTION_TAU: float = CONTRADICTION_TOLERANCE  # 0.1

# Semantic similarity threshold for clustering
SEMANTIC_SIMILARITY_THRESHOLD: float = 0.6

# Minimum stability score (1 - stability deviation)
MIN_STABILITY_SCORE: float = 0.8


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class AxiomCandidate:
    """
    A candidate axiom discovered from decision history.

    Candidates are recurring patterns in decisions that exhibit
    low Galois loss (L < 0.05) and stability under R-C cycles.

    Attributes:
        content: The axiom text (normalized)
        loss: Galois loss (< 0.05 for true axioms)
        stability: How stable over repeated R-C (std dev, lower is better)
        evidence: Mark IDs supporting this axiom
        source_pattern: The recurring pattern that suggests this axiom
        confidence: Computed confidence (1 - loss) * stability_factor
        frequency: How often this pattern appears
        first_seen: Earliest decision with this pattern
        last_seen: Latest decision with this pattern
    """

    content: str
    loss: float
    stability: float
    evidence: list[str]  # Mark IDs
    source_pattern: str
    confidence: float = 0.0
    frequency: int = 1
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_axiom(self) -> bool:
        """True if loss is below axiom threshold."""
        return self.loss < AXIOM_THRESHOLD

    @property
    def stability_score(self) -> float:
        """
        Stability score (0-1, higher is better).

        Converts standard deviation to a score where
        lower deviation = higher score.
        """
        # Stability is std dev, so lower is better
        # Convert to 0-1 score where 1 is perfect stability
        return max(0.0, 1.0 - (self.stability / STABILITY_THRESHOLD))

    def compute_confidence(self) -> float:
        """
        Compute overall confidence in this axiom candidate.

        Factors:
        - Loss (lower = better): (1 - loss)
        - Stability (lower std dev = better): stability_score
        - Frequency (more occurrences = better): log(frequency)
        """
        import math

        loss_factor = 1.0 - self.loss
        stability_factor = self.stability_score
        frequency_factor = min(1.0, math.log(self.frequency + 1) / 3)  # Caps at ~20 occurrences

        self.confidence = loss_factor * 0.5 + stability_factor * 0.3 + frequency_factor * 0.2
        return self.confidence

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "content": self.content,
            "loss": self.loss,
            "stability": self.stability,
            "stability_score": self.stability_score,
            "evidence": self.evidence,
            "source_pattern": self.source_pattern,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "is_axiom": self.is_axiom,
        }


@dataclass
class ContradictionPair:
    """
    A detected contradiction between two axiom candidates.

    Contradiction exists when L(A∪B) > L(A) + L(B) + τ (super-additive loss).

    Attributes:
        axiom_a: First axiom content
        axiom_b: Second axiom content
        loss_a: Galois loss of A
        loss_b: Galois loss of B
        loss_combined: Galois loss of A∪B
        strength: Super-additive excess (how strong the contradiction)
        synthesis_hint: Potential resolution suggested by ghost alternatives
    """

    axiom_a: str
    axiom_b: str
    loss_a: float
    loss_b: float
    loss_combined: float
    strength: float  # L(A∪B) - L(A) - L(B) - τ
    synthesis_hint: str | None = None

    @property
    def is_strong(self) -> bool:
        """Strong contradiction if strength > 0.3."""
        return self.strength > 0.3

    @property
    def type_label(self) -> str:
        """Classify contradiction by strength."""
        if self.strength > 0.5:
            return "IRRECONCILABLE"
        elif self.strength > 0.3:
            return "STRONG"
        elif self.strength > 0.1:
            return "MODERATE"
        else:
            return "WEAK"

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "axiom_a": self.axiom_a,
            "axiom_b": self.axiom_b,
            "loss_a": self.loss_a,
            "loss_b": self.loss_b,
            "loss_combined": self.loss_combined,
            "strength": self.strength,
            "type": self.type_label,
            "synthesis_hint": self.synthesis_hint,
        }


@dataclass
class AxiomDiscoveryResult:
    """
    Complete result of axiom discovery pipeline.

    Contains all discovered candidates, analysis metrics,
    and detected contradictions.
    """

    candidates: list[AxiomCandidate]
    total_decisions_analyzed: int
    time_window_days: int
    contradictions_detected: list[ContradictionPair]
    patterns_found: int
    axioms_discovered: int  # Count where L < 0.05
    duration_ms: float
    user_id: str | None = None

    @property
    def top_axioms(self) -> list[AxiomCandidate]:
        """Get candidates that qualify as axioms (L < 0.05)."""
        return [c for c in self.candidates if c.is_axiom]

    @property
    def has_contradictions(self) -> bool:
        """True if any contradictions were detected."""
        return len(self.contradictions_detected) > 0

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "total_decisions_analyzed": self.total_decisions_analyzed,
            "time_window_days": self.time_window_days,
            "contradictions_detected": [c.to_dict() for c in self.contradictions_detected],
            "patterns_found": self.patterns_found,
            "axioms_discovered": self.axioms_discovered,
            "duration_ms": self.duration_ms,
            "user_id": self.user_id,
            "top_axioms": [c.to_dict() for c in self.top_axioms],
            "has_contradictions": self.has_contradictions,
        }


@dataclass
class DecisionPattern:
    """
    A recurring pattern extracted from decision marks.

    Intermediate type used during pattern extraction.
    """

    pattern: str
    occurrences: int
    mark_ids: list[str]
    first_seen: datetime
    last_seen: datetime


# =============================================================================
# Pipeline Implementation
# =============================================================================


class AxiomDiscoveryPipeline:
    """
    Full axiom discovery pipeline for personal governance.

    Discovers personal axioms from decision history by:
    1. Surfacing decisions from MarkStore
    2. Computing Galois loss for patterns
    3. Identifying fixed points (L < 0.05)
    4. Clustering similar patterns
    5. Detecting contradictions

    Example:
        >>> pipeline = AxiomDiscoveryPipeline()
        >>> result = await pipeline.discover_axioms(
        ...     user_id="kent",
        ...     days=30,
        ...     max_candidates=5,
        ... )
        >>> for axiom in result.top_axioms:
        ...     print(f"L={axiom.loss:.3f}: {axiom.content}")

    Philosophy:
        "You've made 147 decisions this month.
         Here are the 3 principles you never violated — your L0 axioms."
    """

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        computer: GaloisLossComputer | None = None,
        cache: LossCache | None = None,
    ) -> None:
        """
        Initialize axiom discovery pipeline.

        Args:
            mark_store: Optional MarkStore (uses global if None)
            computer: Optional GaloisLossComputer (creates default if None)
            cache: Optional LossCache for caching loss computations
        """
        self._mark_store = mark_store
        self._cache = cache or LossCache()
        self._computer = computer or GaloisLossComputer(cache=self._cache)
        self._discovery_service = AxiomDiscoveryService(
            computer=self._computer,
            cache=self._cache,
        )

    def _get_mark_store(self) -> MarkStore:
        """Get MarkStore (lazy initialization)."""
        if self._mark_store is None:
            from services.witness import get_mark_store

            self._mark_store = get_mark_store()
        return self._mark_store

    async def discover_axioms(
        self,
        user_id: str | None = None,
        days: int = DEFAULT_TIME_WINDOW_DAYS,
        max_candidates: int = 5,
        min_pattern_occurrences: int = MIN_DECISIONS_FOR_PATTERN,
    ) -> AxiomDiscoveryResult:
        """
        Discover personal axioms from decision history.

        Pipeline:
        1. Surface decisions from past N days
        2. Extract recurring patterns
        3. Compute Galois loss for each pattern
        4. Identify fixed points (L < 0.05)
        5. Detect contradictions between candidates
        6. Return top candidates with evidence

        Args:
            user_id: Optional user ID for filtering
            days: Time window in days (default: 30)
            max_candidates: Maximum candidates to return (default: 5)
            min_pattern_occurrences: Minimum times a pattern must appear

        Returns:
            AxiomDiscoveryResult with candidates and contradictions
        """
        import time

        start = time.monotonic()

        # Stage 1: Surface decisions
        logger.info(f"Stage 1: Surfacing decisions from past {days} days")
        decisions = await self._surface_decisions(days=days)
        logger.info(f"Found {len(decisions)} decisions")

        if len(decisions) < min_pattern_occurrences:
            # Not enough decisions for pattern detection
            return AxiomDiscoveryResult(
                candidates=[],
                total_decisions_analyzed=len(decisions),
                time_window_days=days,
                contradictions_detected=[],
                patterns_found=0,
                axioms_discovered=0,
                duration_ms=(time.monotonic() - start) * 1000,
                user_id=user_id,
            )

        # Stage 2: Extract patterns
        logger.info("Stage 2: Extracting decision patterns")
        patterns = self._extract_patterns(decisions, min_pattern_occurrences)
        logger.info(f"Found {len(patterns)} recurring patterns")

        # Stage 3: Compute Galois loss and identify fixed points
        logger.info("Stage 3: Computing Galois loss for patterns")
        candidates = await self._compute_losses_and_identify_fixed_points(
            patterns, decisions, max_candidates
        )
        logger.info(f"Identified {len(candidates)} axiom candidates")

        # Stage 4: Detect contradictions between top candidates
        logger.info("Stage 4: Detecting contradictions")
        contradictions = await self._detect_contradictions(candidates)
        logger.info(f"Found {len(contradictions)} contradictions")

        # Compute final metrics
        axiom_count = sum(1 for c in candidates if c.is_axiom)
        elapsed = (time.monotonic() - start) * 1000

        return AxiomDiscoveryResult(
            candidates=candidates,
            total_decisions_analyzed=len(decisions),
            time_window_days=days,
            contradictions_detected=contradictions,
            patterns_found=len(patterns),
            axioms_discovered=axiom_count,
            duration_ms=elapsed,
            user_id=user_id,
        )

    async def _surface_decisions(self, days: int) -> list[Mark]:
        """
        Surface decisions from MarkStore.

        Queries marks from the past N days that are tagged as decisions
        or contain decision-related content.

        Args:
            days: Number of days to look back

        Returns:
            List of decision marks
        """
        from services.witness import MarkQuery

        store = self._get_mark_store()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Query marks with decision-related tags
        query = MarkQuery(
            after=cutoff,
            tags=("decision", "decide", "chose", "choice", "reasoning"),
        )

        decision_marks = list(store.query(query))

        # Also query marks with "decision" in metadata
        all_query = MarkQuery(after=cutoff)
        for mark in store.query(all_query):
            if mark in decision_marks:
                continue
            # Check if mark has decision-related content
            if self._is_decision_mark(mark):
                decision_marks.append(mark)

        return decision_marks

    def _is_decision_mark(self, mark: Mark) -> bool:
        """
        Determine if a mark represents a decision.

        Checks:
        - Tags include decision-related keywords
        - Metadata contains decision/reasoning fields
        - Response content contains decision patterns
        - Proof claim indicates a decision
        """
        # Check tags first
        if mark.tags:
            decision_tags = {"decision", "decide", "chose", "choice", "reasoning"}
            if any(tag in decision_tags for tag in mark.tags):
                return True

        # Check metadata
        if mark.metadata:
            if "decision" in mark.metadata or "reasoning" in mark.metadata:
                return True
            if mark.metadata.get("type") == "decision":
                return True

        # Check response content
        if mark.response and mark.response.content:
            content_lower = mark.response.content.lower()
            decision_indicators = [
                "decided",
                "chose",
                "choosing",
                "prefer",
                "prioritize",
                "selected",
                "opted",
                "reasoning:",
                "because",
                "therefore",
            ]
            if any(indicator in content_lower for indicator in decision_indicators):
                return True

        # Check proof claim
        if mark.proof and mark.proof.claim:
            return True

        return False

    def _extract_patterns(
        self,
        decisions: list[Mark],
        min_occurrences: int,
    ) -> list[DecisionPattern]:
        """
        Extract recurring value patterns from decisions.

        Uses value phrase extraction to find recurring principles
        across multiple decisions.

        Args:
            decisions: List of decision marks
            min_occurrences: Minimum times a pattern must appear

        Returns:
            List of DecisionPattern with occurrence counts
        """
        # Extract content from each decision
        phrase_to_marks: dict[str, list[tuple[str, datetime]]] = {}

        for mark in decisions:
            content = self._extract_decision_content(mark)
            if not content:
                continue

            # Extract value phrases
            phrases = extract_value_phrases(content)
            for phrase in phrases:
                normalized = phrase.lower().strip()
                if not normalized or len(normalized) < 5:
                    continue

                if normalized not in phrase_to_marks:
                    phrase_to_marks[normalized] = []
                phrase_to_marks[normalized].append((str(mark.id), mark.timestamp))

        # Convert to patterns with occurrence counts
        patterns: list[DecisionPattern] = []
        for phrase, occurrences in phrase_to_marks.items():
            if len(occurrences) >= min_occurrences:
                mark_ids = [m[0] for m in occurrences]
                timestamps = [m[1] for m in occurrences]
                patterns.append(
                    DecisionPattern(
                        pattern=phrase,
                        occurrences=len(occurrences),
                        mark_ids=mark_ids,
                        first_seen=min(timestamps),
                        last_seen=max(timestamps),
                    )
                )

        # Sort by occurrence count (most frequent first)
        patterns.sort(key=lambda p: -p.occurrences)

        return patterns[:MAX_ANALYSIS_CANDIDATES]

    def _extract_decision_content(self, mark: Mark) -> str:
        """
        Extract decision content from a Mark.

        Combines:
        - Response content
        - Proof claim and warrant
        - Metadata decision/reasoning fields
        """
        parts: list[str] = []

        # Response content
        if mark.response and mark.response.content:
            parts.append(mark.response.content)

        # Proof content
        if mark.proof:
            if mark.proof.claim:
                parts.append(mark.proof.claim)
            if mark.proof.warrant:
                parts.append(mark.proof.warrant)

        # Metadata
        if mark.metadata:
            if "decision" in mark.metadata:
                parts.append(str(mark.metadata["decision"]))
            if "reasoning" in mark.metadata:
                parts.append(str(mark.metadata["reasoning"]))
            if "synthesis" in mark.metadata:
                parts.append(str(mark.metadata["synthesis"]))

        return " ".join(parts)

    async def _compute_losses_and_identify_fixed_points(
        self,
        patterns: list[DecisionPattern],
        decisions: list[Mark],
        max_candidates: int,
    ) -> list[AxiomCandidate]:
        """
        Compute Galois loss for patterns and identify fixed points.

        For each pattern:
        1. Compute Galois loss L(pattern)
        2. Check stability under repeated R-C
        3. Create candidate if L < threshold

        Args:
            patterns: Decision patterns to analyze
            decisions: Original decision marks (for evidence)
            max_candidates: Maximum candidates to return

        Returns:
            List of AxiomCandidate sorted by loss
        """
        candidates: list[AxiomCandidate] = []

        for pattern in patterns:
            # Detect fixed point (includes stability check)
            result: FixedPointResult = await detect_fixed_point(
                content=pattern.pattern,
                computer=self._computer,
                threshold=FIXED_POINT_THRESHOLD,
                stability_threshold=STABILITY_THRESHOLD,
            )

            # Create candidate
            candidate = AxiomCandidate(
                content=pattern.pattern.capitalize(),
                loss=result.loss,
                stability=result.stability,
                evidence=pattern.mark_ids[:10],  # Limit evidence
                source_pattern=pattern.pattern,
                frequency=pattern.occurrences,
                first_seen=pattern.first_seen,
                last_seen=pattern.last_seen,
            )
            candidate.compute_confidence()
            candidates.append(candidate)

        # Sort by loss (lowest first = best axioms)
        candidates.sort(key=lambda c: c.loss)

        return candidates[:max_candidates]

    async def _detect_contradictions(
        self,
        candidates: list[AxiomCandidate],
    ) -> list[ContradictionPair]:
        """
        Detect contradictions between axiom candidates.

        A contradiction exists when:
        L(A∪B) > L(A) + L(B) + τ

        This super-additive loss signals that combining A and B
        destroys semantic coherence—they conflict.

        Args:
            candidates: Axiom candidates to check

        Returns:
            List of ContradictionPair for any detected conflicts
        """
        contradictions: list[ContradictionPair] = []

        # Only check candidates that qualify as axioms
        axiom_candidates = [c for c in candidates if c.is_axiom]

        # Check all pairs
        for i, candidate_a in enumerate(axiom_candidates):
            for candidate_b in axiom_candidates[i + 1 :]:
                # Detect contradiction using Galois loss
                analysis = await detect_contradiction(
                    content_a=candidate_a.content,
                    content_b=candidate_b.content,
                    computer=self._computer,
                )

                # Check if super-additive
                if analysis.is_contradiction:
                    contradiction = ContradictionPair(
                        axiom_a=candidate_a.content,
                        axiom_b=candidate_b.content,
                        loss_a=analysis.loss_a,
                        loss_b=analysis.loss_b,
                        loss_combined=analysis.loss_combined,
                        strength=analysis.strength,
                        synthesis_hint=analysis.synthesis_hint.content
                        if analysis.synthesis_hint
                        else None,
                    )
                    contradictions.append(contradiction)

        return contradictions

    async def validate_potential_axiom(
        self,
        content: str,
    ) -> AxiomCandidate:
        """
        Validate if user-provided content qualifies as an axiom.

        Useful for testing whether a proposed axiom would pass
        the L < 0.05 fixed-point test.

        Args:
            content: The potential axiom to validate

        Returns:
            AxiomCandidate with validation results
        """
        result = await detect_fixed_point(
            content=content,
            computer=self._computer,
            threshold=FIXED_POINT_THRESHOLD,
            stability_threshold=STABILITY_THRESHOLD,
        )

        candidate = AxiomCandidate(
            content=content,
            loss=result.loss,
            stability=result.stability,
            evidence=[],
            source_pattern=content.lower(),
            frequency=1,
        )
        candidate.compute_confidence()

        return candidate


# =============================================================================
# Convenience Functions
# =============================================================================


async def discover_personal_axioms(
    days: int = DEFAULT_TIME_WINDOW_DAYS,
    max_candidates: int = 5,
    user_id: str | None = None,
) -> AxiomDiscoveryResult:
    """
    Convenience function to discover personal axioms.

    Example:
        >>> result = await discover_personal_axioms(days=30)
        >>> print(f"Found {result.axioms_discovered} axioms from {result.total_decisions_analyzed} decisions")
    """
    pipeline = AxiomDiscoveryPipeline()
    return await pipeline.discover_axioms(
        user_id=user_id,
        days=days,
        max_candidates=max_candidates,
    )


async def validate_axiom_candidate(content: str) -> tuple[bool, float, float]:
    """
    Validate if content qualifies as an axiom.

    Returns:
        Tuple of (is_axiom, loss, stability)
    """
    pipeline = AxiomDiscoveryPipeline()
    candidate = await pipeline.validate_potential_axiom(content)
    return candidate.is_axiom, candidate.loss, candidate.stability


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_TIME_WINDOW_DAYS",
    "MIN_DECISIONS_FOR_PATTERN",
    "MAX_ANALYSIS_CANDIDATES",
    "CONTRADICTION_TAU",
    # Data types
    "AxiomCandidate",
    "ContradictionPair",
    "AxiomDiscoveryResult",
    "DecisionPattern",
    # Pipeline
    "AxiomDiscoveryPipeline",
    # Convenience functions
    "discover_personal_axioms",
    "validate_axiom_candidate",
]
