"""
Crystal: The Unified Memory Compression Unit.

Crystals are the atomic unit of compressed witness memory. They exist in a hierarchy:
- Level 0 (SESSION): Direct crystallization from marks
- Level 1 (DAY): Compression of level-0 crystals
- Level 2 (WEEK): Compression of level-1 crystals
- Level 3 (EPOCH): Compression of level-2 crystals (milestones)

The Core Laws:
- Law 1 (Mark Immutability): Marks are never deleted—crystals are a lens, not replacement
- Law 2 (Provenance Chain): Every crystal references its sources (marks or crystals)
- Law 3 (Level Consistency): Level N crystals only source from level N-1 (clean DAG)
- Law 4 (Temporal Containment): Crystal time_range contains all source time_ranges
- Law 5 (Compression Monotonicity): Higher levels are always denser (fewer, broader)
- Law 6 (Constitutional Preservation): Constitutional alignment aggregates through compression

The Transformative Insight:
    "Marks are observations. Crystals are insights."

    Experience Crystallization transforms ephemeral events into durable,
    navigable memory. A crystal is not a summary—it's a semantic compression
    that preserves causal structure while reducing volume.

Constitutional Integration (Phase 1: Witness as Constitutional Enforcement):
    Crystals now preserve constitutional metadata through the compression hierarchy.
    ConstitutionalCrystalMeta aggregates principle trends, tracks alignment trajectories,
    and computes trust earned during the crystallized period.

    Formula: trust_earned = Σ(0.02 if alignment > 0.8 else 0.0) for each mark

Philosophy:
    "The garden thrives through pruning. Marks become crystals. Crystals become wisdom."
    "Constitutional compliance compounds through compression."

See: spec/protocols/witness-crystallization.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Any, NewType
from uuid import uuid4

if TYPE_CHECKING:
    from .mark import ConstitutionalAlignment, Mark, MarkId

# =============================================================================
# Type Aliases
# =============================================================================

CrystalId = NewType("CrystalId", str)


def generate_crystal_id() -> CrystalId:
    """Generate a unique Crystal ID."""
    return CrystalId(f"crystal-{uuid4().hex[:12]}")


# =============================================================================
# CrystalLevel Enum
# =============================================================================


class CrystalLevel(IntEnum):
    """
    Hierarchy of crystal compression levels.

    Each level represents a temporal and semantic boundary:
    - SESSION (0): A work session (typically hours)
    - DAY (1): A day's worth of sessions
    - WEEK (2): A week's worth of days
    - EPOCH (3): A milestone or theme (variable duration)

    Higher levels are denser, broader, and more abstract.
    Lower levels are richer, narrower, and more concrete.
    """

    SESSION = 0  # Direct crystallization from marks
    DAY = 1  # Compression of session crystals
    WEEK = 2  # Compression of day crystals
    EPOCH = 3  # Compression of week crystals (milestones)

    @property
    def name_display(self) -> str:
        """Human-friendly name for display."""
        return {
            CrystalLevel.SESSION: "Session",
            CrystalLevel.DAY: "Day",
            CrystalLevel.WEEK: "Week",
            CrystalLevel.EPOCH: "Epoch",
        }[self]

    @property
    def typical_compression_ratio(self) -> tuple[int, int]:
        """Typical compression ratio range for this level."""
        return {
            CrystalLevel.SESSION: (10, 50),  # 10:1 to 50:1 marks
            CrystalLevel.DAY: (5, 20),  # 5:1 to 20:1 session crystals
            CrystalLevel.WEEK: (5, 10),  # 5:1 to 10:1 day crystals
            CrystalLevel.EPOCH: (2, 100),  # Variable for milestones
        }[self]


# =============================================================================
# MoodVector: Affective Signature
# =============================================================================


@dataclass(frozen=True)
class MoodVector:
    """
    Seven-dimensional affective signature of crystallized experience.

    Each dimension is a float in [0, 1]:
    - warmth: Cold/clinical ↔ Warm/engaging (connection)
    - weight: Light/playful ↔ Heavy/serious (gravity)
    - tempo: Slow/deliberate ↔ Fast/urgent (pace)
    - texture: Smooth/flowing ↔ Rough/struggling (friction)
    - brightness: Dim/frustrated ↔ Bright/joyful (affect)
    - saturation: Muted/routine ↔ Vivid/intense (engagement)
    - complexity: Simple/focused ↔ Complex/branching (scope)

    The Insight: Qualia space enables cross-modal retrieval.
    "Find sessions that felt like this one" → vector similarity.
    """

    warmth: float = 0.5
    weight: float = 0.5
    tempo: float = 0.5
    texture: float = 0.5
    brightness: float = 0.5
    saturation: float = 0.5
    complexity: float = 0.5

    def __post_init__(self) -> None:
        """Validate all dimensions are in [0, 1]."""
        for dim in (
            "warmth",
            "weight",
            "tempo",
            "texture",
            "brightness",
            "saturation",
            "complexity",
        ):
            value = getattr(self, dim)
            if not 0.0 <= value <= 1.0:
                object.__setattr__(self, dim, max(0.0, min(1.0, value)))

    @classmethod
    def neutral(cls) -> MoodVector:
        """Return a neutral mood (all 0.5)."""
        return cls()

    @classmethod
    def from_marks(cls, marks: list["Mark"]) -> MoodVector:
        """
        Derive mood from a list of marks.

        Signal aggregation (Pattern 4 from crown-jewel-patterns.md):
        Multiple weak signals → affective signature.
        """
        if not marks:
            return cls.neutral()

        total = len(marks)

        # Count signal markers from mark content
        failures = sum(
            1
            for m in marks
            if "fail" in m.response.content.lower()
            or "error" in m.response.content.lower()
            or any("failure" in str(t).lower() for t in m.tags)
        )
        successes = sum(
            1
            for m in marks
            if "pass" in m.response.content.lower()
            or "success" in m.response.content.lower()
            or any("success" in str(t).lower() for t in m.tags)
        )
        commits = sum(
            1
            for m in marks
            if any("commit" in str(t).lower() for t in m.tags)
            or "commit" in m.response.content.lower()
        )
        tests = sum(1 for m in marks if any("test" in str(t).lower() for t in m.tags))

        # Derive dimensions from signals
        brightness = 0.5 + 0.3 * ((successes - failures) / max(total, 1))
        brightness = max(0.0, min(1.0, brightness))

        # Tempo from event density
        tempo = min(1.0, total / 50)  # Normalize to 50 events = full tempo

        # Weight from test/commit ratio
        weight = 0.3 + 0.4 * (tests / max(total, 1))

        # Complexity from unique origins
        origins = set(m.origin for m in marks)
        complexity = min(1.0, len(origins) / 5)  # 5 origins = full complexity

        # Saturation from activity level
        saturation = min(1.0, total / 30)  # 30 events = full saturation

        # Texture from failure ratio
        texture = 0.5 + 0.3 * (failures / max(total, 1))
        texture = max(0.0, min(1.0, texture))

        # Warmth from commits
        warmth = 0.4 + 0.4 * (commits / max(total, 1))

        return cls(
            warmth=warmth,
            weight=weight,
            tempo=tempo,
            texture=texture,
            brightness=brightness,
            saturation=saturation,
            complexity=complexity,
        )

    def similarity(self, other: MoodVector) -> float:
        """
        Cosine similarity to another mood vector.

        Returns float in [-1, 1] (usually [0, 1] for positive values).
        """
        import math

        a = [
            self.warmth,
            self.weight,
            self.tempo,
            self.texture,
            self.brightness,
            self.saturation,
            self.complexity,
        ]
        b = [
            other.warmth,
            other.weight,
            other.tempo,
            other.texture,
            other.brightness,
            other.saturation,
            other.complexity,
        ]

        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))

        if mag_a == 0 and mag_b == 0:
            return 1.0
        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (mag_a * mag_b)

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "warmth": self.warmth,
            "weight": self.weight,
            "tempo": self.tempo,
            "texture": self.texture,
            "brightness": self.brightness,
            "saturation": self.saturation,
            "complexity": self.complexity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> MoodVector:
        """Create from dictionary."""
        return cls(
            warmth=data.get("warmth", 0.5),
            weight=data.get("weight", 0.5),
            tempo=data.get("tempo", 0.5),
            texture=data.get("texture", 0.5),
            brightness=data.get("brightness", 0.5),
            saturation=data.get("saturation", 0.5),
            complexity=data.get("complexity", 0.5),
        )

    @property
    def dominant_quality(self) -> str:
        """Return the most prominent quality."""
        dims = {
            "warmth": self.warmth,
            "weight": self.weight,
            "tempo": self.tempo,
            "texture": self.texture,
            "brightness": self.brightness,
            "saturation": self.saturation,
            "complexity": self.complexity,
        }
        return max(dims.keys(), key=lambda k: abs(dims[k] - 0.5))


# =============================================================================
# ConstitutionalCrystalMeta: Constitutional Preservation Through Compression
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalCrystalMeta:
    """
    Constitutional metadata preserved through crystal compression.

    When marks are compressed into crystals, this class aggregates
    constitutional alignment data to preserve the constitutional
    character of the crystallized period.

    Philosophy:
        "Constitutional compliance compounds through compression."

        Wisdom isn't just facts—it's principled facts. A crystal that
        represents 50 marks should preserve whether those marks were
        ethical, composable, joyful. Trust accumulates from demonstrated
        constitutional alignment over time.

    Integration:
        - Created by ConstitutionalCrystallizer during compression
        - Used by ConstitutionalTrustComputer to compute trust levels
        - Displayed in ConstitutionalDashboard as crystal-level overview

    The Seven Principles (with weights):
        - ETHICAL: 2.0 (safety first)
        - COMPOSABLE: 1.5 (architecture second)
        - JOY_INDUCING: 1.2 (Kent's aesthetic)
        - TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE: 1.0 each

    Example:
        >>> meta = ConstitutionalCrystalMeta.from_marks(marks)
        >>> print(f"Dominant: {meta.dominant_principles}")
        >>> print(f"Trust earned: {meta.trust_earned}")
    """

    # Top 3 principles in this crystal (by aggregate score)
    dominant_principles: tuple[str, ...]

    # Alignment scores over time (trajectory for sparkline visualization)
    alignment_trajectory: tuple[float, ...]

    # Mean alignment across all source marks
    average_alignment: float

    # Total number of violations (marks below threshold)
    violations_count: int

    # Trust delta earned from this crystal (Article V: Trust Accumulation)
    trust_earned: float

    # Per-principle aggregate scores (for radar chart)
    principle_trends: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_marks(
        cls,
        marks: list["Mark"],
        threshold: float = 0.5,
    ) -> "ConstitutionalCrystalMeta":
        """
        Aggregate constitutional metadata from a list of marks.

        This is the primary factory for creating ConstitutionalCrystalMeta
        during crystal compression. It:
        1. Extracts constitutional alignments from each mark
        2. Computes per-principle aggregate scores
        3. Identifies top 3 dominant principles
        4. Computes trust earned based on alignment quality

        Args:
            marks: List of marks with optional constitutional alignment
            threshold: Compliance threshold (default 0.5)

        Returns:
            ConstitutionalCrystalMeta with aggregated data
        """
        # Extract alignments from marks
        alignments = [m.constitutional for m in marks if m.constitutional is not None]

        if not alignments:
            return cls(
                dominant_principles=(),
                alignment_trajectory=(),
                average_alignment=0.0,
                violations_count=0,
                trust_earned=0.0,
                principle_trends={},
            )

        # Compute per-principle aggregate scores
        principle_totals: dict[str, float] = {}
        principle_counts: dict[str, int] = {}

        for alignment in alignments:
            for principle, score in alignment.principle_scores.items():
                principle = principle.upper()
                principle_totals[principle] = principle_totals.get(principle, 0.0) + score
                principle_counts[principle] = principle_counts.get(principle, 0) + 1

        # Average per principle
        principle_trends = {
            p: principle_totals[p] / principle_counts[p]
            for p in principle_totals
            if principle_counts[p] > 0
        }

        # Identify top 3 dominant principles
        sorted_principles = sorted(
            principle_trends.keys(),
            key=lambda p: -principle_trends[p],
        )
        dominant_principles = tuple(sorted_principles[:3])

        # Alignment trajectory (for sparkline)
        alignment_trajectory = tuple(a.weighted_total for a in alignments)

        # Average alignment
        average_alignment = sum(alignment_trajectory) / len(alignment_trajectory)

        # Count violations
        violations_count = sum(1 for a in alignments if not a.is_compliant)

        # Compute trust earned (Article V: Trust Accumulation)
        # +0.02 for each high-alignment mark (above 0.8)
        trust_earned = sum(0.02 if a.weighted_total > 0.8 else 0.0 for a in alignments)

        return cls(
            dominant_principles=dominant_principles,
            alignment_trajectory=alignment_trajectory,
            average_alignment=average_alignment,
            violations_count=violations_count,
            trust_earned=trust_earned,
            principle_trends=principle_trends,
        )

    @classmethod
    def from_crystals(
        cls,
        crystals: list["Crystal"],
    ) -> "ConstitutionalCrystalMeta":
        """
        Aggregate constitutional metadata from source crystals.

        Used for DAY, WEEK, and EPOCH crystals that aggregate
        lower-level crystals.
        """
        metas = [c.constitutional_meta for c in crystals if c.constitutional_meta is not None]

        if not metas:
            return cls(
                dominant_principles=(),
                alignment_trajectory=(),
                average_alignment=0.0,
                violations_count=0,
                trust_earned=0.0,
                principle_trends={},
            )

        # Aggregate principle trends (weighted by trajectory length)
        principle_totals: dict[str, float] = {}
        principle_weights: dict[str, float] = {}

        for meta in metas:
            weight = len(meta.alignment_trajectory) if meta.alignment_trajectory else 1
            for principle, score in meta.principle_trends.items():
                principle_totals[principle] = principle_totals.get(principle, 0.0) + score * weight
                principle_weights[principle] = principle_weights.get(principle, 0.0) + weight

        principle_trends = {
            p: principle_totals[p] / principle_weights[p]
            for p in principle_totals
            if principle_weights[p] > 0
        }

        # Identify top 3
        sorted_principles = sorted(
            principle_trends.keys(),
            key=lambda p: -principle_trends[p],
        )
        dominant_principles = tuple(sorted_principles[:3])

        # Concatenate trajectories (sample if too long)
        all_trajectories = [t for m in metas for t in m.alignment_trajectory]
        if len(all_trajectories) > 100:
            # Sample to 100 points for visualization
            step = len(all_trajectories) // 100
            all_trajectories = all_trajectories[::step][:100]

        # Aggregate other metrics
        total_weight = (
            sum(len(m.alignment_trajectory) for m in metas if m.alignment_trajectory) or 1
        )
        average_alignment = (
            sum(
                m.average_alignment * len(m.alignment_trajectory)
                for m in metas
                if m.alignment_trajectory
            )
            / total_weight
        )

        violations_count = sum(m.violations_count for m in metas)
        trust_earned = sum(m.trust_earned for m in metas)

        return cls(
            dominant_principles=dominant_principles,
            alignment_trajectory=tuple(all_trajectories),
            average_alignment=average_alignment,
            violations_count=violations_count,
            trust_earned=trust_earned,
            principle_trends=principle_trends,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dominant_principles": list(self.dominant_principles),
            "alignment_trajectory": list(self.alignment_trajectory),
            "average_alignment": self.average_alignment,
            "violations_count": self.violations_count,
            "trust_earned": self.trust_earned,
            "principle_trends": self.principle_trends,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstitutionalCrystalMeta":
        """Create from dictionary."""
        return cls(
            dominant_principles=tuple(data.get("dominant_principles", [])),
            alignment_trajectory=tuple(data.get("alignment_trajectory", [])),
            average_alignment=data.get("average_alignment", 0.0),
            violations_count=data.get("violations_count", 0),
            trust_earned=data.get("trust_earned", 0.0),
            principle_trends=data.get("principle_trends", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        dom = ",".join(self.dominant_principles[:2]) if self.dominant_principles else "none"
        return (
            f"ConstitutionalCrystalMeta("
            f"dominant=[{dom}], "
            f"avg={self.average_alignment:.2f}, "
            f"trust={self.trust_earned:.2f})"
        )


# =============================================================================
# Crystal: The Unified Memory Unit
# =============================================================================


@dataclass(frozen=True)
class Crystal:
    """
    The atomic unit of compressed witness memory.

    A Crystal exists at a level in the compression hierarchy:
    - Level 0 (SESSION): Direct crystallization from marks
    - Level 1 (DAY): Compression of level-0 crystals
    - Level 2 (WEEK): Compression of level-1 crystals
    - Level 3 (EPOCH): Compression of level-2 crystals (milestones)

    Laws (verified at creation):
    - Law 2: source_marks OR source_crystals, never both (provenance clarity)
    - Law 3: Level 0 uses source_marks, Level 1+ uses source_crystals

    A Crystal captures:
    - WHAT happened (insight - semantic compression)
    - WHY it matters (significance)
    - WHAT emerged (principles)
    - WHEN it happened (time_range)
    - HOW it felt (mood)

    Example:
        >>> crystal = Crystal(
        ...     id=generate_crystal_id(),
        ...     level=CrystalLevel.SESSION,
        ...     insight="Completed extinction audit, removed 52K lines",
        ...     significance="Codebase is leaner, focus is sharper",
        ...     principles=("tasteful", "curated"),
        ...     source_marks=tuple(mark_ids),
        ...     time_range=(start, end),
        ...     crystallized_at=datetime.now(),
        ... )
    """

    # Identity
    id: CrystalId = field(default_factory=generate_crystal_id)
    level: CrystalLevel = CrystalLevel.SESSION

    # Content (semantic compression)
    insight: str = ""  # 1-3 sentences capturing the essence
    significance: str = ""  # Why this matters going forward
    principles: tuple[str, ...] = ()  # Principles that emerged

    # Provenance (Law 2: never broken)
    source_marks: tuple["MarkId", ...] = ()  # Level 0: direct mark sources
    source_crystals: tuple[CrystalId, ...] = ()  # Level 1+: crystal sources
    source_kblocks: tuple[str, ...] = ()  # K-Block IDs that contributed to this crystal

    # Temporal bounds
    time_range: tuple[datetime, datetime] | None = None  # What period this covers
    crystallized_at: datetime = field(default_factory=datetime.now)

    # Semantic handles for retrieval
    topics: frozenset[str] = field(default_factory=frozenset)
    mood: MoodVector = field(default_factory=MoodVector.neutral)

    # Metrics
    compression_ratio: float = 1.0  # sources / 1
    confidence: float = 0.8  # Crystallizer's confidence [0, 1]
    token_estimate: int = 0  # For budget calculations

    # Optional session context
    session_id: str = ""

    # Constitutional metadata (Phase 1: Witness as Constitutional Enforcement)
    constitutional_meta: ConstitutionalCrystalMeta | None = None

    def __post_init__(self) -> None:
        """Validate crystal laws."""
        # Law 3: Level consistency
        if self.level == CrystalLevel.SESSION:
            if self.source_crystals and not self.source_marks:
                raise ValueError(
                    "Level 0 (SESSION) crystals must use source_marks, not source_crystals"
                )
        else:
            if self.source_marks and not self.source_crystals:
                raise ValueError(
                    f"Level {self.level.value} crystals must use source_crystals, not source_marks"
                )

    @classmethod
    def from_crystallization(
        cls,
        insight: str,
        significance: str,
        principles: list[str],
        source_marks: list["MarkId"],
        time_range: tuple[datetime, datetime],
        confidence: float = 0.8,
        topics: set[str] | None = None,
        mood: MoodVector | None = None,
        session_id: str = "",
    ) -> Crystal:
        """
        Create a level-0 (SESSION) crystal from crystallization results.

        This is the primary factory for LLM-produced crystals.
        """
        # Estimate tokens from content length
        content_length = len(insight) + len(significance) + sum(len(p) for p in principles)
        token_estimate = content_length // 4 + 50  # Rough estimate

        return cls(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight=insight,
            significance=significance,
            principles=tuple(principles),
            source_marks=tuple(source_marks),
            source_crystals=(),
            source_kblocks=(),
            time_range=time_range,
            crystallized_at=datetime.now(),
            topics=frozenset(topics or set()),
            mood=mood or MoodVector.neutral(),
            compression_ratio=len(source_marks) if source_marks else 1.0,
            confidence=confidence,
            token_estimate=token_estimate,
            session_id=session_id,
        )

    @classmethod
    def from_crystallization_with_kblocks(
        cls,
        insight: str,
        significance: str,
        principles: list[str],
        source_marks: list["MarkId"],
        source_kblocks: list[str],
        time_range: tuple[datetime, datetime],
        confidence: float = 0.8,
        topics: set[str] | None = None,
        mood: MoodVector | None = None,
        session_id: str = "",
    ) -> Crystal:
        """
        Create a level-0 (SESSION) crystal with K-Block provenance.

        This extends from_crystallization() to include K-Block IDs that
        contributed to this crystal. Used when marks originated from
        K-Block bind operations.

        Args:
            insight: 1-3 sentences capturing the essence
            significance: Why this matters going forward
            principles: Principles that emerged
            source_marks: List of MarkIds that were crystallized
            source_kblocks: List of KBlockId strings that contributed
            time_range: The temporal bounds this crystal covers
            confidence: Crystallizer's confidence [0, 1]
            topics: Semantic handles for retrieval
            mood: Affective signature
            session_id: Optional session context

        Returns:
            A level-0 Crystal with K-Block provenance
        """
        content_length = len(insight) + len(significance) + sum(len(p) for p in principles)
        token_estimate = content_length // 4 + 50

        return cls(
            id=generate_crystal_id(),
            level=CrystalLevel.SESSION,
            insight=insight,
            significance=significance,
            principles=tuple(principles),
            source_marks=tuple(source_marks),
            source_crystals=(),
            source_kblocks=tuple(source_kblocks),
            time_range=time_range,
            crystallized_at=datetime.now(),
            topics=frozenset(topics or set()),
            mood=mood or MoodVector.neutral(),
            compression_ratio=len(source_marks) if source_marks else 1.0,
            confidence=confidence,
            token_estimate=token_estimate,
            session_id=session_id,
        )

    @classmethod
    def from_crystals(
        cls,
        insight: str,
        significance: str,
        principles: list[str],
        source_crystals: list[CrystalId],
        level: CrystalLevel,
        confidence: float = 0.8,
        topics: set[str] | None = None,
        mood: MoodVector | None = None,
    ) -> Crystal:
        """
        Create a higher-level crystal from source crystals.

        Used for DAY, WEEK, and EPOCH crystals.
        """
        if level == CrystalLevel.SESSION:
            raise ValueError("Use from_crystallization for SESSION crystals")

        content_length = len(insight) + len(significance) + sum(len(p) for p in principles)
        token_estimate = content_length // 4 + 50

        return cls(
            id=generate_crystal_id(),
            level=level,
            insight=insight,
            significance=significance,
            principles=tuple(principles),
            source_marks=(),
            source_crystals=tuple(source_crystals),
            source_kblocks=(),
            time_range=None,  # Would be computed from source crystals
            crystallized_at=datetime.now(),
            topics=frozenset(topics or set()),
            mood=mood or MoodVector.neutral(),
            compression_ratio=len(source_crystals) if source_crystals else 1.0,
            confidence=confidence,
            token_estimate=token_estimate,
            session_id="",
        )

    def with_constitutional_meta(self, meta: ConstitutionalCrystalMeta) -> "Crystal":
        """
        Return new Crystal with constitutional metadata (immutable pattern).

        This is typically called by ConstitutionalCrystallizer after
        aggregating constitutional alignment data from source marks.
        """
        return Crystal(
            id=self.id,
            level=self.level,
            insight=self.insight,
            significance=self.significance,
            principles=self.principles,
            source_marks=self.source_marks,
            source_crystals=self.source_crystals,
            source_kblocks=self.source_kblocks,
            time_range=self.time_range,
            crystallized_at=self.crystallized_at,
            topics=self.topics,
            mood=self.mood,
            compression_ratio=self.compression_ratio,
            confidence=self.confidence,
            token_estimate=self.token_estimate,
            session_id=self.session_id,
            constitutional_meta=meta,
        )

    def has_kblock_provenance(self) -> bool:
        """Check if this crystal has K-Block provenance."""
        return len(self.source_kblocks) > 0

    def get_kblock_ids(self) -> tuple[str, ...]:
        """Get all K-Block IDs that contributed to this crystal."""
        return self.source_kblocks

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "level": self.level.value,
            "insight": self.insight,
            "significance": self.significance,
            "principles": list(self.principles),
            "source_marks": [str(m) for m in self.source_marks],
            "source_crystals": [str(c) for c in self.source_crystals],
            "source_kblocks": list(self.source_kblocks),
            "time_range": [
                self.time_range[0].isoformat(),
                self.time_range[1].isoformat(),
            ]
            if self.time_range
            else None,
            "crystallized_at": self.crystallized_at.isoformat(),
            "topics": list(self.topics),
            "mood": self.mood.to_dict(),
            "compression_ratio": self.compression_ratio,
            "confidence": self.confidence,
            "token_estimate": self.token_estimate,
            "session_id": self.session_id,
            "constitutional_meta": self.constitutional_meta.to_dict()
            if self.constitutional_meta
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Crystal:
        """Create from dictionary."""
        from .mark import MarkId

        time_range = None
        if data.get("time_range"):
            time_range = (
                datetime.fromisoformat(data["time_range"][0]),
                datetime.fromisoformat(data["time_range"][1]),
            )

        constitutional_meta = (
            ConstitutionalCrystalMeta.from_dict(data["constitutional_meta"])
            if data.get("constitutional_meta")
            else None
        )

        return cls(
            id=CrystalId(data["id"]),
            level=CrystalLevel(data["level"]),
            insight=data.get("insight", ""),
            significance=data.get("significance", ""),
            principles=tuple(data.get("principles", [])),
            source_marks=tuple(MarkId(m) for m in data.get("source_marks", [])),
            source_crystals=tuple(CrystalId(c) for c in data.get("source_crystals", [])),
            source_kblocks=tuple(data.get("source_kblocks", [])),
            time_range=time_range,
            crystallized_at=datetime.fromisoformat(data["crystallized_at"])
            if data.get("crystallized_at")
            else datetime.now(),
            topics=frozenset(data.get("topics", [])),
            mood=MoodVector.from_dict(data.get("mood", {})),
            compression_ratio=data.get("compression_ratio", 1.0),
            confidence=data.get("confidence", 0.8),
            token_estimate=data.get("token_estimate", 0),
            session_id=data.get("session_id", ""),
            constitutional_meta=constitutional_meta,
        )

    @property
    def source_count(self) -> int:
        """Number of sources (marks or crystals)."""
        return len(self.source_marks) or len(self.source_crystals)

    @property
    def duration_minutes(self) -> float | None:
        """Duration of the crystallized period in minutes."""
        if self.time_range:
            return (self.time_range[1] - self.time_range[0]).total_seconds() / 60
        return None

    def __repr__(self) -> str:
        """Concise representation."""
        duration = self.duration_minutes
        duration_str = f"{duration:.1f}min" if duration else "?"
        return (
            f"Crystal("
            f"id={str(self.id)[:12]}..., "
            f"level={self.level.name}, "
            f"sources={self.source_count}, "
            f"duration={duration_str}, "
            f"confidence={self.confidence:.2f})"
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "CrystalId",
    "generate_crystal_id",
    # Enums
    "CrystalLevel",
    # Data classes
    "MoodVector",
    "ConstitutionalCrystalMeta",
    "Crystal",
]
