"""
Crystal Compression: Turn Your Day Into Proof of Intention.

This module provides aggressive compression of daily traces to <10% of original
size while preserving causal rationale. It's the trail-to-crystal-daily-lab
wedge pilot implementation.

Key Principles:
1. COMPRESSION: Crystal size < 10% of trace size
2. PRESERVATION: Causal rationale ("why" chain) stays intact
3. HONESTY: What was dropped is disclosed (Amendment G compliance)

Philosophy:
    "The crystal is Kent's proof of intention. Make it honest and shareable."

    Experience crystallization transforms ephemeral events into durable,
    navigable memory. The crystal is not a summary - it's a semantic
    compression that preserves causal structure while reducing volume.

Compression Strategy:
    1. Causal Chain Extraction: Identify the "why" chain across marks
    2. Redundancy Removal: Similar marks -> representative
    3. Gap Detection: Find provisional/uncertain items
    4. Honesty Preservation: Track what was dropped and why

See: spec/protocols/witness-crystallization.md
See: pilots/trail-to-crystal-daily-lab.md
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .crystal import (
    ConstitutionalCrystalMeta,
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from .honesty import (
    CompressionHonesty,
    CrystalHonestyCalculator,
    get_honesty_calculator,
)
from .mark import (
    Mark,
    MarkId,
)

if TYPE_CHECKING:
    from .crystallizer import Crystallizer

logger = logging.getLogger("kgents.witness.crystal_compression")


# =============================================================================
# Constants
# =============================================================================

# Target compression ratio (crystal should be <10% of original trace size)
TARGET_COMPRESSION_RATIO = 0.10

# Importance weights for mark prioritization
IMPORTANCE_WEIGHTS = {
    "veto": 1.0,  # Mirror Test failures are most important
    "eureka": 0.9,  # Breakthroughs next
    "taste": 0.8,  # Design decisions
    "gotcha": 0.7,  # Traps
    "joy": 0.6,  # Delight moments
    "friction": 0.5,  # Resistance
}

# Default importance for untagged marks
DEFAULT_IMPORTANCE = 0.3

# Minimum similarity threshold for redundancy detection
SIMILARITY_THRESHOLD = 0.85


# =============================================================================
# Compression Result
# =============================================================================


@dataclass
class CausalLink:
    """A causal connection between two marks."""

    source_id: MarkId
    target_id: MarkId
    relation: str  # "causes", "continues", "branches", "fulfills"
    strength: float  # 0.0-1.0, how strong the causal connection is

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "relation": self.relation,
            "strength": self.strength,
        }


@dataclass
class HonestGap:
    """A detected gap or provisional item in the trace."""

    mark_id: MarkId
    description: str
    gap_type: str  # "provisional", "uncertain", "incomplete", "speculative"
    confidence: float  # How confident we are this is a gap

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mark_id": str(self.mark_id),
            "description": self.description,
            "gap_type": self.gap_type,
            "confidence": self.confidence,
        }


@dataclass
class DroppedReason:
    """Explanation for why a mark was dropped."""

    mark_id: MarkId
    reason: str  # "redundant", "low_importance", "tangent", "noise"
    detail: str  # Human-readable explanation
    similar_to: MarkId | None = None  # If redundant, what it's similar to

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mark_id": str(self.mark_id),
            "reason": self.reason,
            "detail": self.detail,
            "similar_to": str(self.similar_to) if self.similar_to else None,
        }


@dataclass
class CompressionResult:
    """
    Result of crystal compression with full honesty disclosure.

    This dataclass captures everything about a compression operation:
    - What was kept (crystal + preserved marks)
    - What was lost (dropped marks + reasons)
    - The causal chain (preserved rationale)
    - Honest gaps (where uncertainty remains)

    Target: compression_ratio < 0.10 (crystal is <10% of trace size)
    """

    # The compressed crystal
    crystal: Crystal

    # Compression metrics
    compression_ratio: float  # 0.0-1.0, target < 0.10
    original_size: int  # Character count of original marks
    compressed_size: int  # Character count of crystal content

    # What was kept
    preserved_marks: list[MarkId]
    preserved_count: int

    # What was lost (honesty)
    dropped_marks: list[MarkId]
    dropped_count: int
    dropped_reasons: list[DroppedReason]

    # The preserved rationale chain
    causal_chain: list[CausalLink]
    chain_summary: str  # Human-readable summary of the why chain

    # Detected gaps/provisional items (honest disclosure)
    honest_gaps: list[HonestGap]
    gaps_summary: str  # "Here's where you were unsure"

    # Honesty metadata (Amendment G)
    honesty: CompressionHonesty

    def __post_init__(self) -> None:
        """Validate compression result."""
        if self.compression_ratio < 0:
            raise ValueError("Compression ratio cannot be negative")

    @property
    def meets_target(self) -> bool:
        """Check if compression met the <10% target."""
        return self.compression_ratio <= TARGET_COMPRESSION_RATIO

    @property
    def quality_tier(self) -> str:
        """Return quality tier based on compression and preservation."""
        if self.compression_ratio <= 0.05:
            return "excellent"  # <5% with causal chain preserved
        elif self.compression_ratio <= 0.10:
            return "good"  # Target met
        elif self.compression_ratio <= 0.20:
            return "acceptable"  # Close to target
        else:
            return "needs_work"  # Didn't compress enough

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "crystal": self.crystal.to_dict(),
            "compression_ratio": self.compression_ratio,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "preserved_marks": [str(m) for m in self.preserved_marks],
            "preserved_count": self.preserved_count,
            "dropped_marks": [str(m) for m in self.dropped_marks],
            "dropped_count": self.dropped_count,
            "dropped_reasons": [r.to_dict() for r in self.dropped_reasons],
            "causal_chain": [c.to_dict() for c in self.causal_chain],
            "chain_summary": self.chain_summary,
            "honest_gaps": [g.to_dict() for g in self.honest_gaps],
            "gaps_summary": self.gaps_summary,
            "honesty": self.honesty.to_dict(),
            "meets_target": self.meets_target,
            "quality_tier": self.quality_tier,
        }


# =============================================================================
# Causal Chain Extractor
# =============================================================================


class CausalChainExtractor:
    """
    Extracts the causal "why" chain from a sequence of marks.

    The causal chain is the preserved rationale - the sequence of
    cause-and-effect relationships that explain how we got here.

    Algorithm:
    1. Build mark dependency graph from explicit links
    2. Infer implicit causal relationships from temporal ordering
    3. Identify chain anchors (eureka, veto, taste decisions)
    4. Trace backwards to find the "why" path
    """

    def extract_chain(self, marks: list[Mark]) -> tuple[list[CausalLink], str]:
        """
        Extract the causal chain from marks.

        Returns:
            Tuple of (causal links, human-readable summary)
        """
        if not marks:
            return [], "No marks to analyze."

        # Sort by timestamp for temporal ordering
        sorted_marks = sorted(marks, key=lambda m: m.timestamp)

        # Build causal links
        links: list[CausalLink] = []

        # First, extract explicit links from mark.links
        for mark in sorted_marks:
            for link in mark.links:
                # Only include links where source is a MarkId (not PlanPath)
                # MarkLink.source can be MarkId | PlanPath, so we need to handle both
                if link.source and not str(link.source).endswith(".md"):
                    links.append(
                        CausalLink(
                            source_id=MarkId(str(link.source)),
                            target_id=link.target,
                            relation=link.relation.name.lower(),
                            strength=1.0,  # Explicit links are strong
                        )
                    )

        # Infer implicit causal links from temporal sequence
        # Marks that are close in time and share tags likely have causal relationship
        for i in range(1, len(sorted_marks)):
            prev_mark = sorted_marks[i - 1]
            curr_mark = sorted_marks[i]

            # Check for tag overlap (indicates related activity)
            shared_tags = set(prev_mark.tags) & set(curr_mark.tags)
            if shared_tags:
                strength = min(1.0, len(shared_tags) * 0.3 + 0.4)
                links.append(
                    CausalLink(
                        source_id=prev_mark.id,
                        target_id=curr_mark.id,
                        relation="continues",
                        strength=strength,
                    )
                )

        # Generate summary
        summary = self._generate_chain_summary(links, sorted_marks)

        return links, summary

    def _generate_chain_summary(self, links: list[CausalLink], marks: list[Mark]) -> str:
        """Generate human-readable summary of the causal chain."""
        if not marks:
            return "Empty trace."

        # Find key moments (eureka, veto, taste)
        key_moments = []
        for mark in marks:
            for tag in mark.tags:
                if tag in ("eureka", "veto", "taste"):
                    key_moments.append((tag, mark.response.content[:50]))
                    break

        if not key_moments:
            return f"A sequence of {len(marks)} marks with {len(links)} causal connections."

        # Build summary from key moments
        parts = []
        for tag, content in key_moments[:3]:  # Top 3
            parts.append(f"{tag}: {content}...")

        return " -> ".join(parts)


# =============================================================================
# Redundancy Detector
# =============================================================================


class RedundancyDetector:
    """
    Detects redundant marks that can be collapsed into representatives.

    Uses content fingerprinting and tag similarity to identify marks
    that say essentially the same thing.
    """

    def __init__(self, similarity_threshold: float = SIMILARITY_THRESHOLD):
        self._threshold = similarity_threshold

    def find_redundant(self, marks: list[Mark]) -> tuple[list[Mark], list[tuple[Mark, Mark]]]:
        """
        Find redundant marks and group them.

        Returns:
            Tuple of (representative marks, list of (redundant, representative) pairs)
        """
        if len(marks) <= 1:
            return marks, []

        # Compute fingerprints for each mark
        fingerprints: dict[MarkId, str] = {}
        for mark in marks:
            fingerprints[mark.id] = self._fingerprint(mark)

        # Group by fingerprint similarity
        representatives: list[Mark] = []
        redundant_pairs: list[tuple[Mark, Mark]] = []
        processed: set[MarkId] = set()

        for mark in marks:
            if mark.id in processed:
                continue

            # This mark becomes a representative
            representatives.append(mark)
            processed.add(mark.id)

            # Find marks similar to this one
            for other in marks:
                if other.id in processed:
                    continue

                similarity = self._similarity(fingerprints[mark.id], fingerprints[other.id])
                if similarity >= self._threshold:
                    redundant_pairs.append((other, mark))  # (redundant, representative)
                    processed.add(other.id)

        return representatives, redundant_pairs

    def _fingerprint(self, mark: Mark) -> str:
        """Generate content fingerprint for a mark."""
        # Combine content and tags for fingerprint
        content = mark.response.content.lower().strip()
        tags = ",".join(sorted(mark.tags))
        combined = f"{content}|{tags}"

        # Hash for compact representation
        return hashlib.md5(combined.encode()).hexdigest()

    def _similarity(self, fp1: str, fp2: str) -> float:
        """Compute similarity between two fingerprints."""
        # Simple character overlap for fingerprint comparison
        # (In production, would use embedding similarity)
        common = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return common / max(len(fp1), len(fp2))


# =============================================================================
# Gap Detector
# =============================================================================


class GapDetector:
    """
    Detects provisional and uncertain items in the trace.

    Looks for signals of uncertainty:
    - Question marks in content
    - Words like "maybe", "perhaps", "unsure"
    - Incomplete sentences
    - Friction tags without resolution
    """

    UNCERTAINTY_SIGNALS = [
        "maybe",
        "perhaps",
        "unsure",
        "unclear",
        "not sure",
        "might",
        "could be",
        "possibly",
        "tentative",
        "provisional",
        "hypothesis",
        "speculative",
    ]

    def detect_gaps(self, marks: list[Mark]) -> list[HonestGap]:
        """Detect gaps and provisional items in marks."""
        gaps: list[HonestGap] = []

        for mark in marks:
            gap = self._analyze_mark_for_gaps(mark)
            if gap:
                gaps.append(gap)

        return gaps

    def _analyze_mark_for_gaps(self, mark: Mark) -> HonestGap | None:
        """Analyze a single mark for gaps or uncertainty."""
        content = mark.response.content.lower()

        # Check for question marks (uncertainty)
        if "?" in content:
            return HonestGap(
                mark_id=mark.id,
                description="Contains open question",
                gap_type="uncertain",
                confidence=0.8,
            )

        # Check for uncertainty signals
        for signal in self.UNCERTAINTY_SIGNALS:
            if signal in content:
                return HonestGap(
                    mark_id=mark.id,
                    description=f"Provisional ({signal})",
                    gap_type="provisional",
                    confidence=0.7,
                )

        # Check for friction without resolution
        if "friction" in mark.tags:
            # Look for subsequent resolution
            # (This is simplified - would check for follow-up marks)
            return HonestGap(
                mark_id=mark.id,
                description="Unresolved friction point",
                gap_type="incomplete",
                confidence=0.5,
            )

        return None


# =============================================================================
# Crystal Compressor
# =============================================================================


class CrystalCompressor:
    """
    Compresses marks to crystal with <10% target ratio and full honesty.

    The compressor applies a multi-stage compression pipeline:
    1. Causal chain extraction (preserve the "why")
    2. Redundancy removal (collapse similar marks)
    3. Importance ranking (keep what matters)
    4. Gap detection (flag provisional items)
    5. Honesty computation (disclose what was lost)

    Target: compression_ratio < 0.10
    """

    def __init__(
        self,
        honesty_calculator: CrystalHonestyCalculator | None = None,
        crystallizer: "Crystallizer | None" = None,
    ):
        """
        Initialize the compressor.

        Args:
            honesty_calculator: Calculator for Amendment G compliance
            crystallizer: LLM-powered crystallizer (optional, for better insights)
        """
        self._honesty = honesty_calculator or get_honesty_calculator()
        self._crystallizer = crystallizer
        self._causal_extractor = CausalChainExtractor()
        self._redundancy_detector = RedundancyDetector()
        self._gap_detector = GapDetector()

    async def compress(
        self,
        marks: list[Mark],
        max_ratio: float = TARGET_COMPRESSION_RATIO,
        session_id: str = "",
    ) -> CompressionResult:
        """
        Compress marks to crystal with honesty.

        Args:
            marks: List of marks to compress
            max_ratio: Target compression ratio (default 0.10)
            session_id: Optional session identifier

        Returns:
            CompressionResult with crystal and full honesty disclosure

        Raises:
            ValueError: If marks list is empty
        """
        if not marks:
            raise ValueError("Cannot compress empty marks list")

        # Sort by timestamp
        marks = sorted(marks, key=lambda m: m.timestamp)

        # Compute original size
        original_size = sum(len(m.response.content) for m in marks)

        # Stage 1: Extract causal chain (this is what we preserve)
        causal_chain, chain_summary = self._causal_extractor.extract_chain(marks)

        # Stage 2: Remove redundancy
        unique_marks, redundant_pairs = self._redundancy_detector.find_redundant(marks)

        # Stage 3: Rank by importance and select top marks
        ranked_marks = self._rank_by_importance(unique_marks)
        kept_marks, dropped_marks = self._select_marks(ranked_marks, original_size, max_ratio)

        # Stage 4: Detect gaps in kept marks
        honest_gaps = self._gap_detector.detect_gaps(kept_marks)
        gaps_summary = self._generate_gaps_summary(honest_gaps)

        # Stage 5: Generate crystal content
        time_range = (marks[0].timestamp, marks[-1].timestamp)
        insight, significance, principles, topics = self._generate_crystal_content(
            kept_marks, chain_summary
        )

        # Compute mood from kept marks
        mood = MoodVector.from_marks(kept_marks)

        # Create the crystal
        crystal = Crystal.from_crystallization(
            insight=insight,
            significance=significance,
            principles=principles,
            source_marks=[m.id for m in kept_marks],
            time_range=time_range,
            confidence=1.0 - (len(dropped_marks) / len(marks)),
            topics=topics,
            mood=mood,
            session_id=session_id,
        )

        # Compute compressed size
        compressed_size = len(insight) + len(significance)

        # Compute compression ratio
        compression_ratio = compressed_size / original_size if original_size > 0 else 0.0

        # Generate dropped reasons
        dropped_reasons = self._generate_dropped_reasons(dropped_marks, redundant_pairs, kept_marks)

        # Compute honesty metrics
        honesty = await self._honesty.compute_honesty(
            original_marks=marks,
            crystal=crystal,
            kept_marks=kept_marks,
        )

        return CompressionResult(
            crystal=crystal,
            compression_ratio=compression_ratio,
            original_size=original_size,
            compressed_size=compressed_size,
            preserved_marks=[m.id for m in kept_marks],
            preserved_count=len(kept_marks),
            dropped_marks=[m.id for m in dropped_marks],
            dropped_count=len(dropped_marks),
            dropped_reasons=dropped_reasons,
            causal_chain=causal_chain,
            chain_summary=chain_summary,
            honest_gaps=honest_gaps,
            gaps_summary=gaps_summary,
            honesty=honesty,
        )

    def _rank_by_importance(self, marks: list[Mark]) -> list[Mark]:
        """Rank marks by importance score."""

        def importance_score(mark: Mark) -> float:
            # Get max importance from tags
            max_tag_importance = DEFAULT_IMPORTANCE
            for tag in mark.tags:
                if tag in IMPORTANCE_WEIGHTS:
                    max_tag_importance = max(max_tag_importance, IMPORTANCE_WEIGHTS[tag])

            # Boost marks with reasoning
            reasoning_boost = 0.1 if mark.metadata.get("reasoning") else 0.0

            # Boost marks with proof
            proof_boost = 0.15 if mark.proof else 0.0

            # Boost marks with constitutional alignment
            constitutional_boost = 0.0
            if mark.constitutional and mark.constitutional.weighted_total > 0.8:
                constitutional_boost = 0.1

            return max_tag_importance + reasoning_boost + proof_boost + constitutional_boost

        return sorted(marks, key=importance_score, reverse=True)

    def _select_marks(
        self,
        ranked_marks: list[Mark],
        original_size: int,
        max_ratio: float,
    ) -> tuple[list[Mark], list[Mark]]:
        """
        Select marks to keep while staying under compression target.

        Strategy: Keep high-importance marks until we hit the budget.
        """
        # Target size for compressed content
        target_crystal_size = int(original_size * max_ratio)

        # Minimum crystal size (ensure we have something)
        min_crystal_size = 100

        # Estimate crystal size per mark (rough heuristic)
        # Crystal insight is ~20% of mark content on average
        COMPRESSION_FACTOR = 0.20

        kept: list[Mark] = []
        dropped: list[Mark] = []
        estimated_crystal_size = 0

        for mark in ranked_marks:
            mark_contribution = int(len(mark.response.content) * COMPRESSION_FACTOR)

            # Always keep at least a few marks
            if len(kept) < 3:
                kept.append(mark)
                estimated_crystal_size += mark_contribution
                continue

            # Check if adding this mark would exceed budget
            if estimated_crystal_size + mark_contribution > target_crystal_size:
                dropped.append(mark)
            else:
                kept.append(mark)
                estimated_crystal_size += mark_contribution

        # Ensure minimum content
        if estimated_crystal_size < min_crystal_size and dropped:
            # Move some dropped marks back to kept
            while dropped and estimated_crystal_size < min_crystal_size:
                mark = dropped.pop(0)
                kept.append(mark)
                estimated_crystal_size += int(len(mark.response.content) * COMPRESSION_FACTOR)

        return kept, dropped

    def _generate_crystal_content(
        self,
        kept_marks: list[Mark],
        chain_summary: str,
    ) -> tuple[str, str, list[str], set[str]]:
        """
        Generate crystal insight, significance, principles, and topics.

        Returns:
            Tuple of (insight, significance, principles, topics)
        """
        # Extract themes from marks
        themes = []
        for mark in kept_marks[:5]:  # Top 5 marks
            content = mark.response.content
            first_sentence = content.split(".")[0][:80]
            themes.append(first_sentence)

        # Generate insight (what happened)
        if len(themes) <= 2:
            insight = f"Worked on: {' and '.join(themes)}."
        else:
            insight = f"Worked on: {', '.join(themes[:2])}, and {len(themes) - 2} more areas."

        # Generate significance (why it matters)
        # Include causal chain summary if meaningful
        if chain_summary and "empty" not in chain_summary.lower():
            significance = f"Key progression: {chain_summary}"
        else:
            eureka_count = sum(1 for m in kept_marks if "eureka" in m.tags)
            veto_count = sum(1 for m in kept_marks if "veto" in m.tags)
            significance_parts = []
            if eureka_count:
                significance_parts.append(
                    f"{eureka_count} breakthrough{'s' if eureka_count > 1 else ''}"
                )
            if veto_count:
                significance_parts.append(
                    f"{veto_count} course correction{'s' if veto_count > 1 else ''}"
                )
            significance = (
                f"Notable: {', '.join(significance_parts)}."
                if significance_parts
                else "Steady progress."
            )

        # Extract principles
        principles = set()
        for mark in kept_marks:
            if mark.constitutional:
                dom = mark.constitutional.dominant_principle
                if dom and dom != "unknown":
                    principles.add(dom.lower())
        if not principles:
            principles.add("tasteful")

        # Extract topics from tags
        topics = set()
        for mark in kept_marks:
            for tag in mark.tags:
                topics.add(tag)

        return insight, significance, list(principles), topics

    def _generate_dropped_reasons(
        self,
        dropped_marks: list[Mark],
        redundant_pairs: list[tuple[Mark, Mark]],
        kept_marks: list[Mark],
    ) -> list[DroppedReason]:
        """Generate human-readable reasons for each dropped mark."""
        reasons: list[DroppedReason] = []
        redundant_ids = {m.id for m, _ in redundant_pairs}
        redundant_to_rep = {m.id: rep.id for m, rep in redundant_pairs}

        for mark in dropped_marks:
            if mark.id in redundant_ids:
                reasons.append(
                    DroppedReason(
                        mark_id=mark.id,
                        reason="redundant",
                        detail="Similar content already captured",
                        similar_to=redundant_to_rep.get(mark.id),
                    )
                )
            elif not mark.tags:
                reasons.append(
                    DroppedReason(
                        mark_id=mark.id,
                        reason="low_importance",
                        detail="Untagged mark with lower priority",
                    )
                )
            else:
                reasons.append(
                    DroppedReason(
                        mark_id=mark.id,
                        reason="compression",
                        detail="Dropped to meet compression target",
                    )
                )

        return reasons

    def _generate_gaps_summary(self, gaps: list[HonestGap]) -> str:
        """Generate human-readable summary of detected gaps."""
        if not gaps:
            return "No provisional items detected. Solid day."

        gap_types = [g.gap_type for g in gaps]
        type_counts: dict[str, int] = {}
        for gt in gap_types:
            type_counts[gt] = type_counts.get(gt, 0) + 1

        parts = []
        for gap_type, count in type_counts.items():
            if gap_type == "uncertain":
                parts.append(f"{count} open question{'s' if count > 1 else ''}")
            elif gap_type == "provisional":
                parts.append(f"{count} tentative item{'s' if count > 1 else ''}")
            elif gap_type == "incomplete":
                parts.append(f"{count} unresolved friction point{'s' if count > 1 else ''}")
            else:
                parts.append(f"{count} {gap_type} item{'s' if count > 1 else ''}")

        return f"Here's where you were unsure: {', '.join(parts)}."


# =============================================================================
# Factory Functions
# =============================================================================


_compressor: CrystalCompressor | None = None


def get_crystal_compressor() -> CrystalCompressor:
    """Get the singleton CrystalCompressor instance."""
    global _compressor
    if _compressor is None:
        _compressor = CrystalCompressor()
    return _compressor


def reset_crystal_compressor() -> None:
    """Reset the singleton (for testing)."""
    global _compressor
    _compressor = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Result types
    "CompressionResult",
    "CausalLink",
    "HonestGap",
    "DroppedReason",
    # Extractors
    "CausalChainExtractor",
    "RedundancyDetector",
    "GapDetector",
    # Main class
    "CrystalCompressor",
    # Factory
    "get_crystal_compressor",
    "reset_crystal_compressor",
    # Constants
    "TARGET_COMPRESSION_RATIO",
    "IMPORTANCE_WEIGHTS",
]
