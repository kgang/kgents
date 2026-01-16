"""
Axiom Discovery Service for Zero Seed Personal Governance.

Discovers personal axioms from decisions/marks through Galois loss analysis.
Axioms are content with L < 0.05 that remain stable under repeated R-C cycles.

Philosophy:
    "Axioms are not stipulated but discovered.
     They are the fixed points of your decision landscape."

Key Concepts:
    - Decision patterns become candidate axioms
    - Galois loss validates fixed-point status
    - L < 0.05 threshold identifies true axioms
    - Stability across iterations confirms discovery

See: spec/protocols/zero-seed1/axiomatics.md
See: plans/enlightened-synthesis/00-master-synthesis.md (A3 GALOIS)
"""

from __future__ import annotations

import asyncio
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .galois import (
    FIXED_POINT_THRESHOLD,
    STABILITY_THRESHOLD,
    FixedPointResult,
    detect_fixed_point,
)
from .galois.galois_loss import (
    GaloisLossComputer,
    LossCache,
)

if TYPE_CHECKING:
    from services.witness import Mark


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Threshold for axiom qualification (L < 0.05)
AXIOM_THRESHOLD: float = 0.05

# Minimum occurrences for pattern to be considered candidate
MIN_PATTERN_OCCURRENCES: int = 3

# Maximum candidates to analyze (performance bound)
MAX_CANDIDATES: int = 20


# -----------------------------------------------------------------------------
# Data Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CandidateAxiom:
    """
    A candidate axiom extracted from decision patterns.

    Candidates are recurring themes/values observed in decisions
    that may qualify as personal axioms after Galois validation.
    """

    content: str
    frequency: int
    source_mark_ids: tuple[str, ...]
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __hash__(self) -> int:
        return hash(self.content)


@dataclass
class DiscoveredAxiom:
    """
    A validated axiom that passed fixed-point detection.

    Attributes:
        content: The axiom statement
        loss: Final Galois loss (< 0.05 for true axioms)
        stability: Standard deviation across R-C iterations
        iterations: Number of stability iterations performed
        confidence: 1 - loss (how axiom-like this is)
        source_decisions: Original decision content that led to discovery
        discovered_at: When the axiom was discovered
    """

    content: str
    loss: float
    stability: float
    iterations: int
    confidence: float
    source_decisions: list[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_axiom(self) -> bool:
        """True if loss is below axiom threshold."""
        return self.loss < AXIOM_THRESHOLD

    @property
    def is_stable(self) -> bool:
        """True if stability is below threshold."""
        return self.stability < STABILITY_THRESHOLD

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "content": self.content,
            "loss": self.loss,
            "stability": self.stability,
            "iterations": self.iterations,
            "confidence": self.confidence,
            "source_decisions": self.source_decisions,
            "discovered_at": self.discovered_at.isoformat(),
            "is_axiom": self.is_axiom,
            "is_stable": self.is_stable,
        }


@dataclass
class DiscoveryReport:
    """
    Report from axiom discovery process.

    Contains all discovered axioms, candidates analyzed,
    and summary statistics.
    """

    discovered: list[DiscoveredAxiom]
    candidates_analyzed: int
    patterns_found: int
    decisions_processed: int
    duration_ms: float

    @property
    def axiom_count(self) -> int:
        """Number of true axioms (L < 0.05)."""
        return sum(1 for a in self.discovered if a.is_axiom)

    @property
    def average_loss(self) -> float:
        """Average loss across all discoveries."""
        if not self.discovered:
            return 1.0
        return sum(a.loss for a in self.discovered) / len(self.discovered)

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "discovered": [a.to_dict() for a in self.discovered],
            "candidates_analyzed": self.candidates_analyzed,
            "patterns_found": self.patterns_found,
            "decisions_processed": self.decisions_processed,
            "duration_ms": self.duration_ms,
            "axiom_count": self.axiom_count,
            "average_loss": self.average_loss,
        }


# -----------------------------------------------------------------------------
# Pattern Extraction
# -----------------------------------------------------------------------------


def extract_decision_content(mark: Mark) -> str:
    """
    Extract decision content from a Mark.

    Looks for decision-related content in:
    1. Response content (primary)
    2. Proof claim if present
    3. Metadata decision fields
    """
    content_parts = []

    # Primary: response content
    if mark.response and mark.response.content:
        content_parts.append(mark.response.content)

    # Secondary: proof claim
    if mark.proof and mark.proof.claim:
        content_parts.append(mark.proof.claim)

    # Tertiary: metadata decision/reasoning
    if mark.metadata:
        if "decision" in mark.metadata:
            content_parts.append(str(mark.metadata["decision"]))
        if "reasoning" in mark.metadata:
            content_parts.append(str(mark.metadata["reasoning"]))

    return " ".join(content_parts)


def extract_value_phrases(text: str) -> list[str]:
    """
    Extract value-laden phrases that might be axioms.

    Looks for patterns like:
    - "X is important"
    - "Always/Never X"
    - "X matters"
    - "Prioritize X over Y"
    - Imperative statements
    """
    phrases = []
    text_lower = text.lower()

    # Pattern 1: Value statements
    value_patterns = [
        r"(\w+(?:\s+\w+){0,3})\s+(?:is|are)\s+(?:important|essential|crucial|fundamental)",
        r"(?:always|never)\s+(\w+(?:\s+\w+){0,5})",
        r"(\w+(?:\s+\w+){0,3})\s+matters",
        r"prioritize\s+(\w+(?:\s+\w+){0,3})",
        r"value\s+(\w+(?:\s+\w+){0,3})",
        r"prefer\s+(\w+(?:\s+\w+){0,5})",
    ]

    for pattern in value_patterns:
        matches = re.findall(pattern, text_lower)
        phrases.extend(matches)

    # Pattern 2: Sentence-level principles (capitalized sentences)
    sentences = re.split(r"[.!?]", text)
    for sent in sentences:
        sent = sent.strip()
        # Short, declarative sentences are often principles
        if 3 <= len(sent.split()) <= 10 and sent[0:1].isupper():
            phrases.append(sent)

    return phrases


def cluster_similar_phrases(phrases: list[str], threshold: float = 0.5) -> list[tuple[str, int]]:
    """
    Cluster similar phrases and count occurrences.

    Uses simple word overlap for similarity.
    Returns list of (representative_phrase, count) tuples.
    """
    if not phrases:
        return []

    # Normalize phrases
    normalized = [p.lower().strip() for p in phrases if p.strip()]

    # Simple word-based clustering
    phrase_words = [set(p.split()) for p in normalized]

    clusters: list[list[int]] = []
    used: set[int] = set()

    for i, words_i in enumerate(phrase_words):
        if i in used:
            continue

        cluster = [i]
        used.add(i)

        for j, words_j in enumerate(phrase_words):
            if j in used or not words_j:
                continue

            # Jaccard similarity
            intersection = len(words_i & words_j)
            union = len(words_i | words_j)
            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                cluster.append(j)
                used.add(j)

        clusters.append(cluster)

    # Pick representative (longest) and count
    results: list[tuple[str, int]] = []
    for cluster in clusters:
        if not cluster:
            continue
        representative = max((normalized[i] for i in cluster), key=len)
        results.append((representative, len(cluster)))

    return sorted(results, key=lambda x: -x[1])


def extract_candidates(
    marks: list[Mark], min_occurrences: int = MIN_PATTERN_OCCURRENCES
) -> list[CandidateAxiom]:
    """
    Extract candidate axioms from a list of decision marks.

    Process:
    1. Extract decision content from each mark
    2. Find value-laden phrases
    3. Cluster similar phrases
    4. Return candidates above occurrence threshold
    """
    all_phrases: list[str] = []
    phrase_to_marks: dict[str, list[str]] = {}

    for mark in marks:
        content = extract_decision_content(mark)
        if not content:
            continue

        phrases = extract_value_phrases(content)
        for phrase in phrases:
            phrase_key = phrase.lower().strip()
            all_phrases.append(phrase_key)
            if phrase_key not in phrase_to_marks:
                phrase_to_marks[phrase_key] = []
            phrase_to_marks[phrase_key].append(str(mark.id))

    # Cluster and filter
    clustered = cluster_similar_phrases(all_phrases)

    candidates: list[CandidateAxiom] = []
    for phrase, count in clustered:
        if count >= min_occurrences:
            # Capitalize for presentation
            display = phrase.capitalize()
            source_ids = phrase_to_marks.get(phrase.lower(), [])[:5]  # Limit source tracking
            candidates.append(
                CandidateAxiom(
                    content=display,
                    frequency=count,
                    source_mark_ids=tuple(source_ids),
                )
            )

    return candidates[:MAX_CANDIDATES]


# -----------------------------------------------------------------------------
# Axiom Discovery Service
# -----------------------------------------------------------------------------


class AxiomDiscoveryService:
    """
    Service for discovering personal axioms from decisions.

    Uses Galois loss to validate that candidate axioms
    are true fixed points (L < 0.05, stable under R-C).

    Example:
        >>> service = AxiomDiscoveryService()
        >>> marks = await mark_store.query(MarkQuery(tags=("decision",)))
        >>> report = await service.discover_axioms(marks)
        >>> for axiom in report.discovered:
        ...     if axiom.is_axiom:
        ...         print(f"Axiom: {axiom.content} (L={axiom.loss:.3f})")
    """

    def __init__(
        self,
        computer: GaloisLossComputer | None = None,
        cache: LossCache | None = None,
    ) -> None:
        """
        Initialize axiom discovery service.

        Args:
            computer: Optional GaloisLossComputer (creates default if None)
            cache: Optional LossCache for caching loss computations
        """
        self._cache = cache or LossCache()
        self._computer = computer or GaloisLossComputer(cache=self._cache)

    async def discover_axioms(
        self,
        decisions: list[Mark],
        min_pattern_occurrences: int = MIN_PATTERN_OCCURRENCES,
    ) -> DiscoveryReport:
        """
        Discover axioms from a list of decision marks.

        Process:
        1. Extract candidate axioms from decision patterns
        2. Validate each candidate via fixed-point detection
        3. Return discovered axioms with metrics

        Args:
            decisions: List of decision marks to analyze
            min_pattern_occurrences: Minimum times a pattern must appear

        Returns:
            DiscoveryReport with discovered axioms and statistics
        """
        import time

        start = time.monotonic()

        # Step 1: Extract candidates
        candidates = extract_candidates(decisions, min_pattern_occurrences)

        # Step 2: Validate each candidate
        discovered: list[DiscoveredAxiom] = []

        for candidate in candidates:
            result = await self.validate_fixed_point(candidate.content)

            # Collect source decision content
            source_decisions: list[str] = []
            for mark in decisions:
                if str(mark.id) in candidate.source_mark_ids:
                    source_decisions.append(extract_decision_content(mark))

            discovered.append(
                DiscoveredAxiom(
                    content=candidate.content,
                    loss=result.loss,
                    stability=result.stability,
                    iterations=result.iterations,
                    confidence=1.0 - result.loss,
                    source_decisions=source_decisions[:3],  # Limit storage
                )
            )

        # Sort by loss (best axioms first)
        discovered.sort(key=lambda a: a.loss)

        elapsed = (time.monotonic() - start) * 1000

        return DiscoveryReport(
            discovered=discovered,
            candidates_analyzed=len(candidates),
            patterns_found=len(candidates),
            decisions_processed=len(decisions),
            duration_ms=elapsed,
        )

    async def validate_fixed_point(
        self,
        content: str,
        threshold: float = AXIOM_THRESHOLD,
        stability_threshold: float = STABILITY_THRESHOLD,
    ) -> FixedPointResult:
        """
        Validate if content is a semantic fixed point.

        A true axiom has:
        1. L < threshold (default 0.05)
        2. Stable under repeated R-C (variance < stability_threshold)

        Args:
            content: Content to validate
            threshold: Loss threshold for fixed point
            stability_threshold: Stability threshold

        Returns:
            FixedPointResult with validation details
        """
        return await detect_fixed_point(
            content=content,
            computer=self._computer,
            threshold=threshold,
            stability_threshold=stability_threshold,
        )

    async def discover_from_text(
        self,
        texts: list[str],
        min_pattern_occurrences: int = MIN_PATTERN_OCCURRENCES,
    ) -> DiscoveryReport:
        """
        Discover axioms from raw text (without Mark structure).

        Useful for analyzing decision logs, journal entries, etc.

        Args:
            texts: List of text content to analyze
            min_pattern_occurrences: Minimum times a pattern must appear

        Returns:
            DiscoveryReport with discovered axioms
        """
        import time

        start = time.monotonic()

        # Extract all phrases
        all_phrases: list[str] = []
        for text in texts:
            phrases = extract_value_phrases(text)
            all_phrases.extend(phrases)

        # Cluster and filter
        clustered = cluster_similar_phrases(all_phrases)
        candidates = [
            (phrase.capitalize(), count)
            for phrase, count in clustered
            if count >= min_pattern_occurrences
        ][:MAX_CANDIDATES]

        # Validate each
        discovered: list[DiscoveredAxiom] = []
        for phrase, count in candidates:
            result = await self.validate_fixed_point(phrase)
            discovered.append(
                DiscoveredAxiom(
                    content=phrase,
                    loss=result.loss,
                    stability=result.stability,
                    iterations=result.iterations,
                    confidence=1.0 - result.loss,
                    source_decisions=[],  # No mark sources for text input
                )
            )

        discovered.sort(key=lambda a: a.loss)
        elapsed = (time.monotonic() - start) * 1000

        return DiscoveryReport(
            discovered=discovered,
            candidates_analyzed=len(candidates),
            patterns_found=len(candidates),
            decisions_processed=len(texts),
            duration_ms=elapsed,
        )


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


async def discover_axioms(decisions: list[Mark]) -> list[DiscoveredAxiom]:
    """
    Convenience function to discover axioms from decisions.

    Returns only the discovered axioms (not full report).
    """
    service = AxiomDiscoveryService()
    report = await service.discover_axioms(decisions)
    return report.discovered


async def validate_axiom(content: str) -> tuple[bool, float]:
    """
    Validate if content qualifies as an axiom.

    Returns:
        Tuple of (is_axiom, loss) where is_axiom is True if L < 0.05
    """
    service = AxiomDiscoveryService()
    result = await service.validate_fixed_point(content)
    return result.is_fixed_point, result.loss


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Constants
    "AXIOM_THRESHOLD",
    "MIN_PATTERN_OCCURRENCES",
    "MAX_CANDIDATES",
    # Data types
    "CandidateAxiom",
    "DiscoveredAxiom",
    "DiscoveryReport",
    # Service
    "AxiomDiscoveryService",
    # Functions
    "discover_axioms",
    "validate_axiom",
    "extract_candidates",
    "extract_value_phrases",
]
