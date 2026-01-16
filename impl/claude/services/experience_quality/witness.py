"""
Experience Quality Operad: Witness Integration.

Quality marks and crystals for witnessing experience quality.

Every quality measurement creates a witness mark.
Quality marks crystallize into quality crystals.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Quality measurement is observation without interference.
    The quality of an experience that measures its own quality
    is a Lawvere fixed point: Q(measure(Q(e))) = Q(e).

See: spec/theory/experience-quality-operad.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

from .measurement import (
    check_floor,
    check_voice,
    generate_recommendation,
    identify_bottleneck,
    measure_arc,
    measure_contrast,
)
from .types import (
    ArcMeasurement,
    ContrastMeasurement,
    Experience,
    ExperienceQuality,
    FloorMeasurement,
    Spec,
    VoiceMeasurement,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Type Aliases
# =============================================================================

QualityMarkId = str
QualityCrystalId = str


def generate_quality_mark_id() -> QualityMarkId:
    """Generate a unique quality mark ID."""
    return f"qmark-{uuid4().hex[:12]}"


def generate_quality_crystal_id() -> QualityCrystalId:
    """Generate a unique quality crystal ID."""
    return f"qcrystal-{uuid4().hex[:12]}"


# =============================================================================
# QualityMark: Witness Mark for Experience Quality
# =============================================================================


@dataclass(frozen=True)
class QualityMark:
    """
    A witness mark for experience quality.

    Records:
    - What the quality was
    - Why it was that quality (detailed measurements)
    - How to improve (bottleneck and recommendation)

    Marks are immutable once created.
    """

    # Identity
    id: QualityMarkId = field(default_factory=generate_quality_mark_id)
    origin: str = "experience-quality-operad"

    # Quality metrics
    quality: ExperienceQuality = field(default_factory=ExperienceQuality)

    # Detailed measurements
    contrast_detail: ContrastMeasurement = field(default_factory=ContrastMeasurement)
    arc_detail: ArcMeasurement = field(default_factory=ArcMeasurement.empty)
    voice_detail: VoiceMeasurement = field(default_factory=VoiceMeasurement.all_pass)
    floor_detail: FloorMeasurement = field(default_factory=FloorMeasurement.empty)

    # Experience context
    experience_id: str = ""
    experience_type: str = ""  # "run", "wave", "session", etc.
    duration_seconds: float = 0.0

    # Diagnosis
    bottleneck: str = ""
    recommendation: str = ""

    # Temporal
    timestamp: datetime = field(default_factory=datetime.now)

    # Tags for categorization
    tags: tuple[str, ...] = ()
    domain: str = ""  # e.g., "wasm_survivors", "daily_lab"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "origin": self.origin,
            "quality": self.quality.to_dict(),
            "contrast_detail": self.contrast_detail.to_dict(),
            "arc_detail": self.arc_detail.to_dict(),
            "voice_detail": self.voice_detail.to_dict(),
            "floor_detail": self.floor_detail.to_dict(),
            "experience_id": self.experience_id,
            "experience_type": self.experience_type,
            "duration_seconds": self.duration_seconds,
            "bottleneck": self.bottleneck,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat(),
            "tags": list(self.tags),
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityMark:
        """Create from dictionary."""
        return cls(
            id=data.get("id", generate_quality_mark_id()),
            origin=data.get("origin", "experience-quality-operad"),
            quality=ExperienceQuality.from_dict(data.get("quality", {})),
            contrast_detail=ContrastMeasurement.from_dict(data.get("contrast_detail", {})),
            arc_detail=ArcMeasurement.from_dict(data.get("arc_detail", {})),
            voice_detail=VoiceMeasurement.from_dict(data.get("voice_detail", {})),
            floor_detail=FloorMeasurement.from_dict(data.get("floor_detail", {})),
            experience_id=data.get("experience_id", ""),
            experience_type=data.get("experience_type", ""),
            duration_seconds=data.get("duration_seconds", 0.0),
            bottleneck=data.get("bottleneck", ""),
            recommendation=data.get("recommendation", ""),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else datetime.now(),
            tags=tuple(data.get("tags", [])),
            domain=data.get("domain", ""),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"QualityMark(id={self.id[:12]}..., "
            f"Q={self.quality.overall:.2f}, "
            f"bottleneck={self.bottleneck})"
        )


# =============================================================================
# QualityMoment: Peak/Trough Snapshot
# =============================================================================


@dataclass(frozen=True)
class QualityMoment:
    """A snapshot of a quality peak or trough moment."""

    mark_id: QualityMarkId
    quality_score: float
    timestamp: datetime
    description: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mark_id": self.mark_id,
            "quality_score": self.quality_score,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityMoment:
        """Create from dictionary."""
        return cls(
            mark_id=data.get("mark_id", ""),
            quality_score=data.get("quality_score", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else datetime.now(),
            description=data.get("description", ""),
        )


# =============================================================================
# QualityCrystal: Compressed Quality Proof
# =============================================================================


@dataclass(frozen=True)
class QualityCrystal:
    """
    Compressed quality proof for an experience.

    Crystals compress multiple quality marks into a summary:
    - Overall quality and trend
    - Dimension summaries
    - Peak and trough moments
    - Recommendations

    Crystals are the semantic compression of quality history.
    """

    # Identity
    id: QualityCrystalId = field(default_factory=generate_quality_crystal_id)

    # Summary metrics
    overall_quality: float = 0.0
    quality_trend: Literal["improving", "stable", "declining"] = "stable"

    # Dimension summaries (human-readable)
    contrast_summary: str = ""
    arc_summary: str = ""
    voice_summary: str = ""
    floor_summary: str = ""

    # Key moments
    quality_peaks: tuple[QualityMoment, ...] = ()
    quality_troughs: tuple[QualityMoment, ...] = ()

    # Recommendations
    primary_recommendation: str = ""
    secondary_recommendations: tuple[str, ...] = ()

    # Compression metadata
    source_mark_ids: tuple[QualityMarkId, ...] = ()
    source_mark_count: int = 0
    compression_ratio: float = 1.0

    # Temporal
    time_range: tuple[datetime, datetime] | None = None
    crystallized_at: datetime = field(default_factory=datetime.now)

    # Domain
    domain: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "overall_quality": self.overall_quality,
            "quality_trend": self.quality_trend,
            "contrast_summary": self.contrast_summary,
            "arc_summary": self.arc_summary,
            "voice_summary": self.voice_summary,
            "floor_summary": self.floor_summary,
            "quality_peaks": [p.to_dict() for p in self.quality_peaks],
            "quality_troughs": [t.to_dict() for t in self.quality_troughs],
            "primary_recommendation": self.primary_recommendation,
            "secondary_recommendations": list(self.secondary_recommendations),
            "source_mark_ids": list(self.source_mark_ids),
            "source_mark_count": self.source_mark_count,
            "compression_ratio": self.compression_ratio,
            "time_range": [
                self.time_range[0].isoformat(),
                self.time_range[1].isoformat(),
            ]
            if self.time_range
            else None,
            "crystallized_at": self.crystallized_at.isoformat(),
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityCrystal:
        """Create from dictionary."""
        time_range = None
        if data.get("time_range"):
            time_range = (
                datetime.fromisoformat(data["time_range"][0]),
                datetime.fromisoformat(data["time_range"][1]),
            )

        return cls(
            id=data.get("id", generate_quality_crystal_id()),
            overall_quality=data.get("overall_quality", 0.0),
            quality_trend=data.get("quality_trend", "stable"),
            contrast_summary=data.get("contrast_summary", ""),
            arc_summary=data.get("arc_summary", ""),
            voice_summary=data.get("voice_summary", ""),
            floor_summary=data.get("floor_summary", ""),
            quality_peaks=tuple(QualityMoment.from_dict(p) for p in data.get("quality_peaks", [])),
            quality_troughs=tuple(
                QualityMoment.from_dict(t) for t in data.get("quality_troughs", [])
            ),
            primary_recommendation=data.get("primary_recommendation", ""),
            secondary_recommendations=tuple(data.get("secondary_recommendations", [])),
            source_mark_ids=tuple(data.get("source_mark_ids", [])),
            source_mark_count=data.get("source_mark_count", 0),
            compression_ratio=data.get("compression_ratio", 1.0),
            time_range=time_range,
            crystallized_at=datetime.fromisoformat(data["crystallized_at"])
            if data.get("crystallized_at")
            else datetime.now(),
            domain=data.get("domain", ""),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"QualityCrystal(id={self.id[:12]}..., "
            f"Q={self.overall_quality:.2f}, "
            f"trend={self.quality_trend}, "
            f"sources={self.source_mark_count})"
        )


# =============================================================================
# Witness Functions
# =============================================================================


async def witness_quality(
    experience: Experience,
    spec: Spec | None = None,
) -> QualityMark:
    """
    Witness the quality of an experience.

    Creates an immutable mark that records:
    - What the quality was
    - Why it was that quality
    - How to improve

    This is async to support potential LLM-based analysis in the future.
    """
    spec = spec or Spec.empty()

    # Measure all dimensions
    contrast = measure_contrast(experience)
    arc = measure_arc(experience)
    voice = check_voice(experience, spec)
    floor = check_floor(experience, experience.domain)

    # Compute overall quality
    quality = ExperienceQuality(
        contrast=contrast.overall,
        arc_coverage=arc.coverage,
        voice_adversarial=voice.adversarial.passed,
        voice_creative=voice.creative.passed,
        voice_advocate=voice.advocate.passed,
        floor_passed=floor.passed,
    )

    # Identify bottleneck and generate recommendation
    bottleneck = identify_bottleneck(quality, contrast, arc, voice, floor)
    recommendation = generate_recommendation(bottleneck)

    # Create the mark
    mark = QualityMark(
        quality=quality,
        contrast_detail=contrast,
        arc_detail=arc,
        voice_detail=voice,
        floor_detail=floor,
        experience_id=experience.id,
        experience_type=experience.type,
        duration_seconds=experience.duration,
        bottleneck=bottleneck,
        recommendation=recommendation,
        domain=experience.domain,
        tags=("quality", experience.type, experience.domain),
    )

    # In production, this would emit the mark to the witness system
    # await emit_mark(mark)

    return mark


async def crystallize_quality(
    marks: list[QualityMark],
    domain: str = "",
) -> QualityCrystal:
    """
    Compress quality marks into a crystal.

    Aggregates:
    - Overall quality and trend
    - Dimension summaries
    - Peak and trough moments
    - Recommendations
    """
    if not marks:
        return QualityCrystal(domain=domain)

    # Extract qualities
    qualities = [m.quality for m in marks]

    # Compute overall (mean)
    overall = sum(q.overall for q in qualities) / len(qualities)

    # Trend analysis
    trend: Literal["improving", "stable", "declining"] = "stable"
    if len(qualities) >= 3:
        third = len(qualities) // 3
        early = sum(q.overall for q in qualities[:third]) / third
        late = sum(q.overall for q in qualities[-third:]) / third

        if late > early + 0.05:
            trend = "improving"
        elif late < early - 0.05:
            trend = "declining"

    # Find peaks and troughs
    sorted_by_quality = sorted(marks, key=lambda m: m.quality.overall)
    troughs = sorted_by_quality[:3]
    peaks = sorted_by_quality[-3:]

    peak_moments = tuple(
        QualityMoment(
            mark_id=m.id,
            quality_score=m.quality.overall,
            timestamp=m.timestamp,
            description=f"Peak: Q={m.quality.overall:.2f}",
        )
        for m in reversed(peaks)
    )

    trough_moments = tuple(
        QualityMoment(
            mark_id=m.id,
            quality_score=m.quality.overall,
            timestamp=m.timestamp,
            description=f"Trough: Q={m.quality.overall:.2f}, bottleneck={m.bottleneck}",
        )
        for m in troughs
    )

    # Summarize dimensions
    contrast_summary = _summarize_contrast([m.contrast_detail for m in marks])
    arc_summary = _summarize_arc([m.arc_detail for m in marks])
    voice_summary = _summarize_voice([m.voice_detail for m in marks])
    floor_summary = _summarize_floor([m.floor_detail for m in marks])

    # Generate recommendations
    primary_recommendation, secondary = _generate_crystal_recommendations(marks)

    # Compute time range
    timestamps = [m.timestamp for m in marks]
    time_range = (min(timestamps), max(timestamps)) if timestamps else None

    # Determine domain
    crystal_domain = domain or (marks[0].domain if marks else "")

    return QualityCrystal(
        overall_quality=overall,
        quality_trend=trend,
        contrast_summary=contrast_summary,
        arc_summary=arc_summary,
        voice_summary=voice_summary,
        floor_summary=floor_summary,
        quality_peaks=peak_moments,
        quality_troughs=trough_moments,
        primary_recommendation=primary_recommendation,
        secondary_recommendations=secondary,
        source_mark_ids=tuple(m.id for m in marks),
        source_mark_count=len(marks),
        compression_ratio=len(marks) / 1,  # 1 crystal per N marks
        time_range=time_range,
        domain=crystal_domain,
    )


# =============================================================================
# Summary Generation Helpers
# =============================================================================


def _summarize_contrast(contrasts: list[ContrastMeasurement]) -> str:
    """Generate a human-readable contrast summary."""
    if not contrasts:
        return "No contrast data"

    overall = sum(c.overall for c in contrasts) / len(contrasts)

    # Find weakest dimension across all measurements
    dimension_scores: dict[str, list[float]] = {
        "breath": [],
        "scarcity": [],
        "tempo": [],
        "stakes": [],
        "anticipation": [],
        "reward": [],
        "identity": [],
    }

    for c in contrasts:
        dimension_scores["breath"].append(c.breath)
        dimension_scores["scarcity"].append(c.scarcity)
        dimension_scores["tempo"].append(c.tempo)
        dimension_scores["stakes"].append(c.stakes)
        dimension_scores["anticipation"].append(c.anticipation)
        dimension_scores["reward"].append(c.reward)
        dimension_scores["identity"].append(c.identity)

    avg_scores = {dim: sum(scores) / len(scores) for dim, scores in dimension_scores.items()}
    weakest = min(avg_scores, key=lambda k: avg_scores[k])

    level = "High" if overall > 0.6 else ("Moderate" if overall > 0.3 else "Low")
    return f"{level} variety (avg {overall:.2f}) with weak {weakest} contrast"


def _summarize_arc(arcs: list[ArcMeasurement]) -> str:
    """Generate a human-readable arc summary."""
    if not arcs:
        return "No arc data"

    avg_coverage = sum(a.coverage for a in arcs) / len(arcs)
    crisis_rate = sum(1 for a in arcs if a.has_crisis) / len(arcs)
    resolution_rate = sum(1 for a in arcs if a.has_resolution) / len(arcs)

    parts = [f"Avg coverage {avg_coverage:.2f}"]

    if crisis_rate > 0.8:
        parts.append("strong crisis presence")
    elif crisis_rate < 0.3:
        parts.append("needs more crisis moments")

    if resolution_rate > 0.8:
        parts.append("clear resolutions")
    elif resolution_rate < 0.3:
        parts.append("resolutions often missing")

    return ", ".join(parts)


def _summarize_voice(voices: list[VoiceMeasurement]) -> str:
    """Generate a human-readable voice summary."""
    if not voices:
        return "No voice data"

    adv_rate = sum(1 for v in voices if v.adversarial.passed) / len(voices)
    cre_rate = sum(1 for v in voices if v.creative.passed) / len(voices)
    adv_rate_pct = adv_rate * 100
    cre_rate_pct = cre_rate * 100

    parts = []
    if adv_rate > 0.9:
        parts.append("Adversarial approved")
    elif adv_rate < 0.5:
        parts.append(f"Adversarial concerns ({adv_rate_pct:.0f}% pass)")

    if cre_rate > 0.7:
        parts.append("Creative approved")
    elif cre_rate < 0.3:
        parts.append(f"Creative concerns ({cre_rate_pct:.0f}% pass)")

    adv_rate_2 = sum(1 for v in voices if v.advocate.passed) / len(voices)
    if adv_rate_2 > 0.8:
        parts.append("Advocate approved")
    elif adv_rate_2 < 0.5:
        parts.append(f"Advocate concerns ({adv_rate_2 * 100:.0f}% pass)")

    return ", ".join(parts) if parts else "All voices aligned"


def _summarize_floor(floors: list[FloorMeasurement]) -> str:
    """Generate a human-readable floor summary."""
    if not floors:
        return "No floor data"

    pass_rate = sum(1 for f in floors if f.passed) / len(floors)

    if pass_rate == 1.0:
        return "All floor checks passed"
    elif pass_rate > 0.9:
        return f"Floor mostly passed ({pass_rate * 100:.0f}%)"
    else:
        # Find most common failures
        failure_counts: dict[str, int] = {}
        for f in floors:
            for failure in f.failures:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1

        if failure_counts:
            top_failure = max(failure_counts, key=lambda k: failure_counts[k])
            return f"Floor issues: {top_failure} ({pass_rate * 100:.0f}% pass rate)"

        return f"Floor pass rate: {pass_rate * 100:.0f}%"


def _generate_crystal_recommendations(
    marks: list[QualityMark],
) -> tuple[str, tuple[str, ...]]:
    """Generate recommendations from crystal data."""
    if not marks:
        return ("No data for recommendations", ())

    # Count bottleneck occurrences
    bottleneck_counts: dict[str, int] = {}
    for m in marks:
        if m.bottleneck:
            bottleneck_counts[m.bottleneck] = bottleneck_counts.get(m.bottleneck, 0) + 1

    if not bottleneck_counts:
        return ("Quality is generally good - maintain current approach", ())

    # Sort by frequency
    sorted_bottlenecks = sorted(bottleneck_counts.keys(), key=lambda k: -bottleneck_counts[k])

    primary = generate_recommendation(sorted_bottlenecks[0])
    secondary = tuple(generate_recommendation(b) for b in sorted_bottlenecks[1:4])

    return (primary, secondary)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "QualityMarkId",
    "QualityCrystalId",
    "generate_quality_mark_id",
    "generate_quality_crystal_id",
    # Mark
    "QualityMark",
    "QualityMoment",
    # Crystal
    "QualityCrystal",
    # Functions
    "witness_quality",
    "crystallize_quality",
]
