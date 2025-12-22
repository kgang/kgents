"""
Trail Bridge: Convert Context Perception Trails to Witness Marks.

Bridges the typed-hypergraph navigation (Context Perception) with the
witness ledger (Witness Crown Jewel), enabling trails to serve as
evidence in ASHC proofs.

Philosophy:
    "The trail IS evidence. The mark IS the witness."

A trail represents behavioral evidence - what paths were explored,
what edges were followed, what annotations were made. This bridge
converts that exploration into a Mark that can be used as evidence.

Evidence Tier:
    Trails are EMPIRICAL evidence (Tier 2). They show what was actually
    done, not what should theoretically work. This makes them stronger
    than AESTHETIC but weaker than CATEGORICAL.

See: spec/protocols/context-perception.md §10
See: spec/protocols/witness-primitives.md

Teaching:
    gotcha: Trails are immutable. When converting to Mark, the trail
            is captured at a point in time. Subsequent trail modifications
            create new Marks linked via CONTINUES relation.
            (Evidence: test_trail_bridge.py::test_trail_immutability_preserved)

    gotcha: Evidence strength is derived from trail characteristics:
            - Step count (more steps = stronger exploration)
            - Diversity (different edge types = wider investigation)
            - Annotations (human notes = intentional exploration)
            (Evidence: test_trail_bridge.py::test_evidence_strength_computation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .mark import (
    MarkId,
    NPhase,
    generate_mark_id,
)

if TYPE_CHECKING:
    from protocols.agentese.contexts.self_context import Trail


# =============================================================================
# Evidence Types
# =============================================================================


class EvidenceTier:
    """Evidence tiers for ASHC integration."""

    CATEGORICAL = 1  # Mathematical (laws hold)
    EMPIRICAL = 2  # Scientific (ASHC runs, trails)
    AESTHETIC = 3  # Hardy criteria (inevitability, etc.)
    GENEALOGICAL = 4  # Git history
    SOMATIC = 5  # Mirror Test (felt sense)


@dataclass(frozen=True)
class TrailEvidence:
    """
    Evidence extracted from a trail.

    Contains:
    - Computed evidence strength
    - Principle signals detected in exploration patterns
    - Commitment level derived from trail diversity
    """

    trail_id: str
    trail_name: str
    step_count: int
    unique_paths: int
    unique_edges: int
    annotation_count: int
    evidence_strength: str  # "weak" | "moderate" | "strong" | "definitive"
    principles_signaled: list[tuple[str, float]]  # [(principle, strength)]
    commitment_level: str  # "tentative" | "moderate" | "strong" | "definitive"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "trail_id": self.trail_id,
            "trail_name": self.trail_name,
            "step_count": self.step_count,
            "unique_paths": self.unique_paths,
            "unique_edges": self.unique_edges,
            "annotation_count": self.annotation_count,
            "evidence_strength": self.evidence_strength,
            "principles_signaled": [
                {"principle": p, "strength": s} for p, s in self.principles_signaled
            ],
            "commitment_level": self.commitment_level,
        }


# =============================================================================
# Trail Analysis
# =============================================================================


def analyze_trail(trail: "Trail") -> TrailEvidence:
    """
    Analyze a trail to extract evidence characteristics.

    Examines:
    - Step count (exploration depth)
    - Path diversity (unique nodes visited)
    - Edge diversity (different edge types used)
    - Annotation density (intentionality signals)

    Returns:
        TrailEvidence with computed characteristics
    """
    step_count = len(trail.steps)
    unique_paths = len({s.node_path for s in trail.steps})
    unique_edges = len({s.edge_type for s in trail.steps if s.edge_type})

    # Count annotations (step-level + trail-level)
    annotation_count = len(trail.annotations) + sum(1 for s in trail.steps if s.annotations)

    # Compute evidence strength
    evidence_strength = _compute_evidence_strength(
        step_count, unique_paths, unique_edges, annotation_count
    )

    # Detect principle signals from exploration patterns
    principles_signaled = _detect_principles(
        step_count, unique_paths, unique_edges, annotation_count
    )

    # Compute commitment level
    commitment_level = _compute_commitment(
        step_count, unique_paths, annotation_count, evidence_strength
    )

    return TrailEvidence(
        trail_id=trail.id,
        trail_name=trail.name,
        step_count=step_count,
        unique_paths=unique_paths,
        unique_edges=unique_edges,
        annotation_count=annotation_count,
        evidence_strength=evidence_strength,
        principles_signaled=principles_signaled,
        commitment_level=commitment_level,
    )


def _compute_evidence_strength(
    step_count: int, unique_paths: int, unique_edges: int, annotation_count: int
) -> str:
    """
    Compute evidence strength from trail characteristics.

    Scoring:
    - Steps >= 3: +1 point
    - Steps >= 7: +1 point
    - Annotations >= 1: +1 point
    - Annotations >= 3: +1 point
    - Unique paths >= 3: +1 point
    - Unique edges >= 2: +1 point

    Mapping:
    - 5+ points: definitive
    - 3-4 points: strong
    - 1-2 points: moderate
    - 0 points: weak
    """
    score = 0

    if step_count >= 3:
        score += 1
    if step_count >= 7:
        score += 1

    if annotation_count >= 1:
        score += 1
    if annotation_count >= 3:
        score += 1

    if unique_paths >= 3:
        score += 1
    if unique_edges >= 2:
        score += 1

    if score >= 5:
        return "definitive"
    elif score >= 3:
        return "strong"
    elif score >= 1:
        return "moderate"
    else:
        return "weak"


def _detect_principles(
    step_count: int, unique_paths: int, unique_edges: int, annotation_count: int
) -> list[tuple[str, float]]:
    """
    Detect principle signals from exploration patterns.

    Patterns:
    - Many diverse edges → COMPOSABLE (agents combine well)
    - Depth-first exploration → CURATED (intentional selection)
    - Annotations → ETHICAL (transparent reasoning)
    - Breadth exploration → HETERARCHICAL (not fixed hierarchy)
    """
    signals: list[tuple[str, float]] = []

    # COMPOSABLE: Many different edge types
    if unique_edges >= 3:
        signals.append(("composable", 0.8))
    elif unique_edges >= 2:
        signals.append(("composable", 0.5))

    # CURATED: Deep exploration (many steps, focused paths)
    if step_count >= 5 and unique_paths <= step_count * 0.6:
        signals.append(("curated", 0.7))

    # ETHICAL: Annotations show transparency
    if annotation_count >= 2:
        signals.append(("ethical", 0.8))
    elif annotation_count >= 1:
        signals.append(("ethical", 0.5))

    # HETERARCHICAL: Breadth exploration
    if unique_paths >= step_count * 0.8:
        signals.append(("heterarchical", 0.6))

    # GENERATIVE: Long trails with few loops suggest derivation
    if step_count >= 7 and unique_paths >= step_count * 0.7:
        signals.append(("generative", 0.6))

    return signals


def _compute_commitment(
    step_count: int, unique_paths: int, annotation_count: int, evidence_strength: str
) -> str:
    """
    Compute commitment level based on trail and evidence characteristics.

    Commitment reflects how much the explorer invested in this trail.
    """
    if evidence_strength == "definitive" and annotation_count >= 3:
        return "definitive"
    elif evidence_strength in ("definitive", "strong") and step_count >= 5:
        return "strong"
    elif step_count >= 3 or annotation_count >= 1:
        return "moderate"
    else:
        return "tentative"


# =============================================================================
# Mark Creation
# =============================================================================


@dataclass(frozen=True)
class TrailMark:
    """
    A Mark created from a Trail.

    Simplified Mark structure for trail evidence.
    The full Mark type is complex; this captures what's needed for trails.
    """

    id: MarkId
    origin: str  # "context_perception"
    trail_id: str
    trail_name: str
    created_at: datetime
    phase: NPhase
    evidence: TrailEvidence
    content: str  # Human-readable trail
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict for bus publishing."""
        return {
            "id": str(self.id),
            "origin": self.origin,
            "trail_id": self.trail_id,
            "trail_name": self.trail_name,
            "created_at": self.created_at.isoformat(),
            "phase": self.phase.value,
            "evidence": self.evidence.to_dict(),
            "content": self.content,
            "metadata": self.metadata,
        }


def convert_trail_to_mark(
    trail: "Trail",
    claim: str | None = None,
    phase: NPhase = NPhase.SENSE,
) -> TrailMark:
    """
    Convert a Trail to a TrailMark for witness ledger.

    Args:
        trail: The trail to convert
        claim: Optional claim this trail supports
        phase: N-Phase this trail was captured in (default: SENSE)

    Returns:
        TrailMark ready for persistence and bus publishing
    """
    # Analyze the trail
    evidence = analyze_trail(trail)

    # Build content from trail's outline format
    content = trail.as_outline()

    # Build metadata
    metadata: dict[str, Any] = {
        "trail_id": trail.id,
        "step_count": evidence.step_count,
        "unique_paths": evidence.unique_paths,
        "unique_edges": evidence.unique_edges,
        "evidence_tier": EvidenceTier.EMPIRICAL,
        "principles_signaled": [p[0] for p in evidence.principles_signaled],
    }

    if claim:
        metadata["claim"] = claim

    return TrailMark(
        id=generate_mark_id(),
        origin="context_perception",
        trail_id=trail.id,
        trail_name=trail.name,
        created_at=datetime.now(),
        phase=phase,
        evidence=evidence,
        content=content,
        metadata=metadata,
    )


# =============================================================================
# Bus Integration
# =============================================================================


async def emit_trail_as_mark(
    trail: "Trail",
    claim: str | None = None,
    phase: NPhase = NPhase.SENSE,
) -> TrailMark:
    """
    Convert trail to mark and emit to witness bus.

    Args:
        trail: The trail to emit
        claim: Optional claim this trail supports
        phase: N-Phase context

    Returns:
        The created TrailMark
    """
    from .bus import WitnessTopics, get_synergy_bus

    # Convert
    mark = convert_trail_to_mark(trail, claim, phase)

    # Emit to bus
    bus = get_synergy_bus()
    await bus.publish(WitnessTopics.TRAIL_CAPTURED, mark.to_dict())

    return mark


__all__ = [
    "EvidenceTier",
    "TrailEvidence",
    "TrailMark",
    "analyze_trail",
    "convert_trail_to_mark",
    "emit_trail_as_mark",
]
