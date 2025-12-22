"""
Witness Bridge: Transform CommitTeaching → Witness Mark.

Phase 5 of Git Archaeology Backfill: Witness Integration.

This module bridges archaeology teachings to the Witness system,
creating retrospective marks from significant commits.

The transformation:
    CommitTeaching              →  Mark (Witness)
    ─────────────────────       ───────────────────────────
    teaching.insight        →   response.content
    commit.sha              →   metadata["commit"]
    category                →   tags
    features                →   metadata["features"]

Design decisions:
- Use GENEALOGICAL evidence tier (from spec/protocols/witness-supersession.md)
- Deterministic mark IDs for idempotent re-runs
- Fire-and-forget async persistence via WitnessPersistence

See: plans/git-archaeology-backfill.md (Phase 4: Witness Integration)
See: services/witness/persistence.py
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Sequence

from services.witness.mark import (
    EvidenceTier,
    Mark,
    MarkId,
    NPhase,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
)

from .teaching_extractor import CommitTeaching

if TYPE_CHECKING:
    from services.witness.persistence import MarkResult, WitnessPersistence


# =============================================================================
# Constants
# =============================================================================

ARCHAEOLOGY_ORIGIN = "archaeology"
ARCHAEOLOGY_LINEAGE_TAG = "archaeology_backfill"


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class CrystallizationResult:
    """Result of crystallizing teachings to Witness marks."""

    total_teachings: int
    marks_created: int
    marks_skipped: int  # Already existed (idempotent)
    errors: list[str]
    mark_ids: list[str]


# =============================================================================
# Bridge Functions
# =============================================================================


def teaching_to_mark(teaching: CommitTeaching) -> Mark:
    """
    Transform a CommitTeaching into a Witness Mark.

    The mark captures:
    - WHAT: The teaching insight
    - WHY: Genealogical evidence from git history
    - WHEN: The commit timestamp
    - WHERE: The affected features/files

    Args:
        teaching: A CommitTeaching from the archaeology extractor

    Returns:
        A Mark ready for persistence
    """
    # Deterministic ID for idempotent re-runs
    mark_id = generate_deterministic_mark_id(teaching)

    # Build proof with genealogical evidence
    proof = Proof(
        data=f"commit:{teaching.commit.sha[:8]}",
        warrant="Git history is evidence of past decisions",
        claim=teaching.teaching.insight,
        backing=f"Commit message: {teaching.commit.message[:100]}",
        qualifier="historically",
        rebuttals=(),
        tier=EvidenceTier.GENEALOGICAL,
        principles=_infer_principles(teaching),
    )

    # Build stimulus from commit
    stimulus = Stimulus(
        kind="git",
        content=teaching.commit.message,
        source="git_archaeology",
        metadata={
            "sha": teaching.commit.sha,
            "author": teaching.commit.author,
            "files_changed": list(teaching.commit.files_changed[:10]),
        },
    )

    # Build response (the teaching insight)
    response = Response(
        kind="thought",
        content=teaching.teaching.insight,
        success=True,
        metadata={
            "severity": teaching.teaching.severity,
            "category": teaching.category,
            "features": list(teaching.features),
        },
    )

    # Build umwelt (archaeological observer)
    umwelt = UmweltSnapshot(
        observer_id="archaeology",
        role="archaeologist",
        capabilities=frozenset({"observe", "read"}),
        perceptions=frozenset({"git", "history"}),
        trust_level=0,  # Read-only, historical
    )

    # Build tags
    tags = (
        ARCHAEOLOGY_LINEAGE_TAG,
        teaching.category,
        f"severity:{teaching.teaching.severity}",
    )

    # Create the mark
    return Mark(
        id=mark_id,
        origin=ARCHAEOLOGY_ORIGIN,
        stimulus=stimulus,
        response=response,
        umwelt=umwelt,
        links=(),  # No causal links for backfilled marks
        timestamp=teaching.commit.timestamp,
        phase=NPhase.REFLECT,  # Archaeological analysis is reflection
        walk_id=None,
        proof=proof,
        tags=tags,
        metadata={
            "commit_sha": teaching.commit.sha,
            "commit_type": teaching.commit.commit_type,
            "features": list(teaching.features),
            "source_evidence": teaching.teaching.evidence,
        },
    )


def generate_deterministic_mark_id(teaching: CommitTeaching) -> MarkId:
    """
    Generate a deterministic mark ID for idempotent re-runs.

    Pattern: arch-{sha[:8]}-{insight_hash[:8]}

    This ensures running crystallize twice won't create duplicate marks.
    """
    insight_hash = hashlib.sha256(teaching.teaching.insight.encode()).hexdigest()[:8]
    return MarkId(f"arch-{teaching.commit.sha[:8]}-{insight_hash}")


def _infer_principles(teaching: CommitTeaching) -> tuple[str, ...]:
    """Infer which constitution principles relate to this teaching."""
    principles: list[str] = []

    # Category-based inference
    if teaching.category == "gotcha":
        principles.append("ethical")  # Learning from mistakes
    elif teaching.category == "pattern":
        principles.append("composable")  # Patterns are reusable
        principles.append("generative")  # Patterns generate implementations
    elif teaching.category == "decision":
        principles.append("tasteful")  # Decisions require judgment
    elif teaching.category in ("warning", "critical"):
        principles.append("curated")  # Warnings help curation

    # Severity-based inference
    if teaching.teaching.severity == "critical":
        principles.append("ethical")  # Critical issues have ethical weight

    return tuple(set(principles))


async def crystallize_teachings_to_witness(
    teachings: Sequence[CommitTeaching],
    persistence: "WitnessPersistence",
    dry_run: bool = False,
) -> CrystallizationResult:
    """
    Crystallize commit teachings as Witness marks.

    This is the main entry point for Phase 5 integration.

    Args:
        teachings: Sequence of CommitTeaching objects
        persistence: WitnessPersistence instance for storage
        dry_run: If True, don't actually persist (just report what would happen)

    Returns:
        CrystallizationResult with statistics
    """
    marks_created = 0
    marks_skipped = 0
    errors: list[str] = []
    mark_ids: list[str] = []

    for teaching in teachings:
        try:
            mark = teaching_to_mark(teaching)

            if dry_run:
                mark_ids.append(str(mark.id))
                marks_created += 1
                continue

            # Check if mark already exists (idempotent)
            existing = await persistence.get_mark(str(mark.id))
            if existing:
                marks_skipped += 1
                continue

            # Save the mark
            result = await persistence.save_mark(
                action=mark.response.content,
                reasoning=mark.proof.backing if mark.proof else None,
                principles=list(mark.proof.principles) if mark.proof else [],
                author="archaeology",
                parent_mark_id=None,
            )

            mark_ids.append(result.mark_id)
            marks_created += 1

        except Exception as e:
            errors.append(f"Error crystallizing {teaching.commit.sha[:8]}: {e}")

    return CrystallizationResult(
        total_teachings=len(teachings),
        marks_created=marks_created,
        marks_skipped=marks_skipped,
        errors=errors,
        mark_ids=mark_ids,
    )


def generate_crystallization_report(result: CrystallizationResult) -> str:
    """Generate a human-readable report of crystallization results."""
    lines = [
        "Archaeological Crystallization Report",
        "=" * 40,
        "",
        f"Total teachings analyzed: {result.total_teachings}",
        f"Marks created: {result.marks_created}",
        f"Marks skipped (already exist): {result.marks_skipped}",
        "",
    ]

    if result.errors:
        lines.extend(
            [
                "Errors:",
                *[f"  - {e}" for e in result.errors[:10]],
            ]
        )
        if len(result.errors) > 10:
            lines.append(f"  ... and {len(result.errors) - 10} more")
        lines.append("")

    if result.mark_ids and len(result.mark_ids) <= 10:
        lines.extend(
            [
                "Created marks:",
                *[f"  - {mid}" for mid in result.mark_ids],
            ]
        )
    elif result.mark_ids:
        lines.extend(
            [
                f"Created {len(result.mark_ids)} marks",
                f"  First: {result.mark_ids[0]}",
                f"  Last: {result.mark_ids[-1]}",
            ]
        )

    return "\n".join(lines)


__all__ = [
    "ARCHAEOLOGY_ORIGIN",
    "ARCHAEOLOGY_LINEAGE_TAG",
    "CrystallizationResult",
    "teaching_to_mark",
    "generate_deterministic_mark_id",
    "crystallize_teachings_to_witness",
    "generate_crystallization_report",
]
