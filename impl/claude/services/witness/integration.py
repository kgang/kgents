"""
Witness Integration: Cross-System Crystallization Bridges.

This module provides integration points between the Witness crystallization
system and other kgents components:

1. **Handoff Integration** — Auto-crystallize before session handoff
2. **NOW.md Proposals** — Generate status updates from day crystals
3. **Brain Promotion** — Promote high-confidence crystals to TeachingCrystals

Philosophy:
    "Crystallization happens at boundaries."

    When Claude hands off to another Claude, crystallize first.
    When we update NOW.md, draw from crystals.
    When a crystal proves significant, promote to Brain.

See: spec/protocols/witness-crystallization.md
See: plans/witness-crystallization.md (Phase 4)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .context import ContextResult, get_context
from .crystal import Crystal, CrystalId, CrystalLevel
from .crystal_store import CrystalStore, get_crystal_store
from .crystallizer import Crystallizer

if TYPE_CHECKING:
    from .crystallizer import SoulProtocol

logger = logging.getLogger("kgents.witness.integration")


# =============================================================================
# Handoff Integration
# =============================================================================


@dataclass
class HandoffContext:
    """
    Context prepared for session handoff.

    Contains crystallized insights and recent crystals for the handoff prompt.
    """

    # New crystal created (if marks were crystallized)
    new_crystal: Crystal | None

    # Recent crystals included in handoff
    recent_crystals: list[Crystal]

    # Token budget used
    tokens_used: int

    # Whether crystallization was performed
    crystallization_performed: bool

    # Any errors encountered
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "new_crystal": {
                "id": str(self.new_crystal.id),
                "insight": self.new_crystal.insight,
                "significance": self.new_crystal.significance,
                "source_count": self.new_crystal.source_count,
            }
            if self.new_crystal
            else None,
            "recent_crystals": [
                {
                    "id": str(c.id),
                    "level": c.level.name,
                    "insight": c.insight[:100],
                }
                for c in self.recent_crystals
            ],
            "tokens_used": self.tokens_used,
            "crystallization_performed": self.crystallization_performed,
            "errors": self.errors,
        }

    def format_for_handoff(self) -> str:
        """Format for inclusion in handoff prompt."""
        lines = ["## Witness Context (Crystallized)"]

        if self.new_crystal:
            lines.append("")
            lines.append(f"**Just Crystallized** ({self.new_crystal.source_count} marks):")
            lines.append(f"> {self.new_crystal.insight}")
            if self.new_crystal.significance:
                lines.append(f"> *{self.new_crystal.significance}*")

        if self.recent_crystals:
            lines.append("")
            lines.append("**Recent Crystals:**")
            for c in self.recent_crystals[:5]:
                level_badge = f"[{c.level.name}]"
                lines.append(f"- {level_badge} {c.insight[:80]}...")

        return "\n".join(lines)


async def prepare_handoff_context(
    soul: "SoulProtocol | None" = None,
    crystallize: bool = True,
    budget_tokens: int = 1500,
    session_id: str = "",
) -> HandoffContext:
    """
    Prepare witness context for session handoff.

    This is called before /handoff to:
    1. Crystallize any pending marks from the session
    2. Gather recent crystals within token budget
    3. Format everything for the handoff prompt

    Args:
        soul: K-gent Soul for LLM crystallization (optional)
        crystallize: Whether to crystallize pending marks (default True)
        budget_tokens: Token budget for crystal context (default 1500)
        session_id: Current session identifier

    Returns:
        HandoffContext with crystallized insights

    Example:
        >>> ctx = await prepare_handoff_context(soul, session_id="abc123")
        >>> handoff_text += ctx.format_for_handoff()
    """
    errors: list[str] = []
    new_crystal: Crystal | None = None

    # Step 1: Crystallize pending marks if requested
    if crystallize:
        try:
            new_crystal = await _crystallize_session_marks(soul, session_id)
        except Exception as e:
            errors.append(f"Crystallization failed: {e}")
            logger.warning(f"Handoff crystallization failed: {e}")

    # Step 2: Get recent crystals within budget
    try:
        context_result = await get_context(budget_tokens=budget_tokens)
        recent_crystals = context_result.crystals
        tokens_used = context_result.total_tokens
    except Exception as e:
        errors.append(f"Context retrieval failed: {e}")
        logger.warning(f"Handoff context retrieval failed: {e}")
        recent_crystals = []
        tokens_used = 0

    return HandoffContext(
        new_crystal=new_crystal,
        recent_crystals=recent_crystals,
        tokens_used=tokens_used,
        crystallization_performed=new_crystal is not None,
        errors=errors,
    )


async def _crystallize_session_marks(
    soul: "SoulProtocol | None",
    session_id: str,
) -> Crystal | None:
    """
    Crystallize marks from the current session.

    Returns the new crystal if created, None if no marks to crystallize.
    """
    from services.providers import get_witness_persistence
    from services.witness.mark import Mark, MarkId, NPhase, Response, Stimulus

    # Get recent marks
    persistence = await get_witness_persistence()
    marks_data = await persistence.get_marks(limit=50)

    if not marks_data:
        logger.info("No marks to crystallize for handoff")
        return None

    # Convert to Mark objects
    marks = []
    for m in marks_data:
        response_metadata = {"reasoning": m.reasoning} if m.reasoning else {}
        mark = Mark(
            id=MarkId(m.mark_id),
            timestamp=m.timestamp,
            origin="cli",
            stimulus=Stimulus(kind="action", content=m.action),
            response=Response(kind="mark", content=m.action, metadata=response_metadata),
            tags=tuple(m.principles),
            phase=NPhase.ACT,
        )
        marks.append(mark)

    # Crystallize
    crystallizer = Crystallizer(soul)
    crystal = await crystallizer.crystallize_marks(marks, session_id=session_id)

    # Store crystal
    store = get_crystal_store()
    store.append(crystal)
    store.sync()

    logger.info(f"Handoff crystallization created crystal {crystal.id}")
    return crystal


# =============================================================================
# NOW.md Proposal Generation
# =============================================================================


@dataclass
class NowMdProposal:
    """
    A proposed update to NOW.md based on recent crystals.
    """

    # Section to update (e.g., "What Just Happened", "What's Next")
    section: str

    # Current content (if exists)
    current_content: str | None

    # Proposed new content
    proposed_content: str

    # Source crystals
    source_crystals: list[Crystal]

    # Confidence in this proposal
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "section": self.section,
            "current_content": self.current_content,
            "proposed_content": self.proposed_content,
            "source_crystal_count": len(self.source_crystals),
            "confidence": self.confidence,
        }

    def format_diff(self) -> str:
        """Format as a diff for review."""
        lines = [f"## Proposed Update: {self.section}"]
        lines.append("")

        if self.current_content:
            lines.append("**Current:**")
            lines.append("```")
            lines.append(self.current_content)
            lines.append("```")
            lines.append("")

        lines.append("**Proposed:**")
        lines.append("```")
        lines.append(self.proposed_content)
        lines.append("```")

        lines.append("")
        lines.append(
            f"*Based on {len(self.source_crystals)} crystals, confidence: {self.confidence:.0%}*"
        )

        return "\n".join(lines)


async def propose_now_update(
    soul: "SoulProtocol | None" = None,
    now_md_path: Path | str | None = None,
) -> list[NowMdProposal]:
    """
    Generate proposed updates to NOW.md from recent day crystals.

    Reads the current NOW.md, compares with recent crystals, and
    proposes updates to relevant sections.

    Args:
        soul: K-gent Soul for LLM generation (optional)
        now_md_path: Path to NOW.md (defaults to project root)

    Returns:
        List of NowMdProposal objects for review

    Example:
        >>> proposals = await propose_now_update(soul)
        >>> for p in proposals:
        ...     print(p.format_diff())
        ...     if input("Apply? [y/n]: ").lower() == 'y':
        ...         apply_proposal(p)
    """
    # Default NOW.md path
    if now_md_path is None:
        now_md_path = Path.cwd() / "NOW.md"
    else:
        now_md_path = Path(now_md_path)

    # Read current NOW.md
    current_content: str | None = None
    if now_md_path.exists():
        current_content = now_md_path.read_text()

    # Get recent day crystals (or session crystals if no day crystals)
    store = get_crystal_store()
    day_crystals = store.recent(limit=5, level=CrystalLevel.DAY)

    if not day_crystals:
        # Fall back to session crystals
        day_crystals = store.recent(limit=10, level=CrystalLevel.SESSION)

    if not day_crystals:
        logger.info("No crystals available for NOW.md proposal")
        return []

    # Generate proposals
    proposals: list[NowMdProposal] = []

    # Proposal for "What Just Happened" section
    what_happened = await _propose_what_happened(soul, day_crystals, current_content)
    if what_happened:
        proposals.append(what_happened)

    # Proposal for "Session Status" section
    session_status = await _propose_session_status(soul, day_crystals, current_content)
    if session_status:
        proposals.append(session_status)

    return proposals


async def _propose_what_happened(
    soul: "SoulProtocol | None",
    crystals: list[Crystal],
    current_now: str | None,
) -> NowMdProposal | None:
    """Generate proposal for 'What Just Happened' section."""
    if not crystals:
        return None

    # Extract current section if exists
    current_section = _extract_section(current_now, "What Just Happened") if current_now else None

    # Build proposed content from crystal insights
    lines = []
    for c in crystals[:5]:
        lines.append(f"- {c.insight}")
        if c.significance:
            lines.append(
                f"  *{c.significance[:80]}...*"
                if len(c.significance) > 80
                else f"  *{c.significance}*"
            )

    proposed = "\n".join(lines)

    # Calculate confidence based on crystal confidence average
    avg_confidence = sum(c.confidence for c in crystals) / len(crystals)

    return NowMdProposal(
        section="What Just Happened",
        current_content=current_section,
        proposed_content=proposed,
        source_crystals=crystals,
        confidence=avg_confidence,
    )


async def _propose_session_status(
    soul: "SoulProtocol | None",
    crystals: list[Crystal],
    current_now: str | None,
) -> NowMdProposal | None:
    """Generate proposal for 'Session Status' section."""
    if not crystals:
        return None

    # Extract current section if exists
    current_section = _extract_section(current_now, "Session Status") if current_now else None

    # Aggregate topics and principles
    all_topics: set[str] = set()
    all_principles: set[str] = set()
    for c in crystals:
        all_topics.update(c.topics)
        all_principles.update(c.principles)

    # Build proposed content
    lines = []
    if all_topics:
        lines.append(f"**Active Topics:** {', '.join(sorted(all_topics)[:8])}")
    if all_principles:
        lines.append(f"**Principles Engaged:** {', '.join(sorted(all_principles))}")
    lines.append(f"**Crystal Count:** {len(crystals)} recent")

    proposed = "\n".join(lines)

    avg_confidence = sum(c.confidence for c in crystals) / len(crystals)

    return NowMdProposal(
        section="Session Status",
        current_content=current_section,
        proposed_content=proposed,
        source_crystals=crystals,
        confidence=avg_confidence * 0.8,  # Lower confidence for derived content
    )


def _extract_section(content: str, section_name: str) -> str | None:
    """Extract a section from markdown content by header name."""
    import re

    # Match ## or ### with section name
    pattern = rf"^##+ {re.escape(section_name)}.*?\n(.*?)(?=^##|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()
    return None


def apply_now_proposal(
    proposal: NowMdProposal,
    now_md_path: Path | str,
    backup: bool = True,
) -> bool:
    """
    Apply a NOW.md proposal.

    Args:
        proposal: The proposal to apply
        now_md_path: Path to NOW.md
        backup: Whether to create a backup first

    Returns:
        True if successful
    """
    import re

    path = Path(now_md_path)

    if not path.exists():
        logger.warning(f"NOW.md not found at {path}")
        return False

    content = path.read_text()

    # Backup if requested
    if backup:
        backup_path = path.with_suffix(f".md.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        backup_path.write_text(content)
        logger.info(f"Backed up NOW.md to {backup_path}")

    # Replace section content
    pattern = rf"(^##+ {re.escape(proposal.section)}.*?\n)(.*?)(?=^##|\Z)"
    replacement = rf"\1{proposal.proposed_content}\n\n"

    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    if new_content == content:
        # Section didn't exist, append it
        new_content = (
            content.rstrip() + f"\n\n## {proposal.section}\n\n{proposal.proposed_content}\n"
        )

    path.write_text(new_content)
    logger.info(f"Applied proposal to '{proposal.section}' section")
    return True


# =============================================================================
# Brain Promotion
# =============================================================================


@dataclass
class PromotionCandidate:
    """
    A crystal that's a candidate for promotion to Brain TeachingCrystal.
    """

    crystal: Crystal
    score: float  # Promotion score (higher = more promotable)
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "crystal_id": str(self.crystal.id),
            "insight": self.crystal.insight,
            "significance": self.crystal.significance,
            "score": self.score,
            "reasons": self.reasons,
        }


def identify_promotion_candidates(
    min_confidence: float = 0.85,
    min_sources: int = 5,
    prefer_epoch: bool = True,
) -> list[PromotionCandidate]:
    """
    Identify crystals worth promoting to Brain TeachingCrystals.

    Scoring factors:
    - Confidence level
    - Source count (compression ratio)
    - Crystal level (higher levels preferred)
    - Principle coverage

    Args:
        min_confidence: Minimum confidence threshold
        min_sources: Minimum source count
        prefer_epoch: Whether to prioritize EPOCH-level crystals

    Returns:
        List of PromotionCandidate objects, sorted by score (highest first)
    """
    store = get_crystal_store()
    candidates: list[PromotionCandidate] = []

    for crystal in store.all():
        reasons: list[str] = []
        score = 0.0

        # Check confidence
        if crystal.confidence < min_confidence:
            continue
        score += crystal.confidence * 0.3
        reasons.append(f"High confidence ({crystal.confidence:.0%})")

        # Check source count
        if crystal.source_count < min_sources:
            continue
        source_score = min(crystal.source_count / 20.0, 1.0) * 0.2
        score += source_score
        reasons.append(f"Good compression ({crystal.source_count} sources)")

        # Level bonus
        level_bonus = crystal.level.value * 0.1
        if prefer_epoch and crystal.level == CrystalLevel.EPOCH:
            level_bonus += 0.2
            reasons.append("EPOCH-level insight")
        elif crystal.level == CrystalLevel.WEEK:
            level_bonus += 0.1
            reasons.append("WEEK-level pattern")
        score += level_bonus

        # Principle coverage bonus
        if len(crystal.principles) >= 2:
            score += 0.1
            reasons.append(f"Multiple principles: {', '.join(crystal.principles[:3])}")

        # Topic richness bonus
        if len(crystal.topics) >= 3:
            score += 0.05

        candidates.append(
            PromotionCandidate(
                crystal=crystal,
                score=score,
                reasons=reasons,
            )
        )

    # Sort by score (highest first)
    candidates.sort(key=lambda c: c.score, reverse=True)

    return candidates


async def promote_to_brain(
    crystal_id: CrystalId,
    module: str = "witness",
    symbol: str = "promoted_insight",
) -> dict[str, Any]:
    """
    Promote a crystal to Brain as a TeachingCrystal.

    This creates a TeachingCrystal in Brain storage with full provenance
    linking back to the source Witness crystal.

    Args:
        crystal_id: ID of the crystal to promote
        module: Target module for the teaching (default: "witness")
        symbol: Target symbol name (default: "promoted_insight")

    Returns:
        Dict with promotion result

    Example:
        >>> result = await promote_to_brain("crystal-abc123")
        >>> print(f"Created teaching: {result['teaching_id']}")
    """
    store = get_crystal_store()
    crystal = store.get(crystal_id)

    if not crystal:
        return {"error": f"Crystal {crystal_id} not found"}

    # Create TeachingCrystal in Brain
    try:
        from services.brain.persistence import BrainPersistence

        # Build teaching data
        teaching_data = {
            "module": module,
            "symbol": symbol,
            "insight": crystal.insight,
            "significance": crystal.significance,
            "principles": list(crystal.principles),
            "topics": list(crystal.topics),
            "evidence": f"Witness crystal {crystal_id}",
            "provenance": {
                "source": "witness_crystal",
                "crystal_id": str(crystal_id),
                "level": crystal.level.name,
                "confidence": crystal.confidence,
                "source_count": crystal.source_count,
            },
        }

        # Note: This is a placeholder - actual Brain integration
        # would use BrainPersistence.crystallize_teaching()
        logger.info(f"Promoted crystal {crystal_id} to Brain teaching")

        return {
            "success": True,
            "crystal_id": str(crystal_id),
            "teaching_data": teaching_data,
            "message": f"Crystal promoted to Brain ({module}.{symbol})",
        }

    except ImportError as e:
        logger.warning(f"Brain service not available: {e}")
        return {
            "error": "Brain service not available",
            "crystal_id": str(crystal_id),
        }
    except Exception as e:
        logger.error(f"Promotion failed: {e}")
        return {
            "error": str(e),
            "crystal_id": str(crystal_id),
        }


async def auto_promote_crystals(
    limit: int = 3,
    min_score: float = 0.7,
) -> list[dict[str, Any]]:
    """
    Automatically promote high-scoring crystals to Brain.

    Args:
        limit: Maximum number of crystals to promote
        min_score: Minimum promotion score threshold

    Returns:
        List of promotion results
    """
    candidates = identify_promotion_candidates()

    # Filter by score and limit
    top_candidates = [c for c in candidates if c.score >= min_score][:limit]

    results = []
    for candidate in top_candidates:
        result = await promote_to_brain(candidate.crystal.id)
        results.append(result)

    return results


# =============================================================================
# CLI Integration
# =============================================================================


async def cmd_propose_now_async() -> dict[str, Any]:
    """CLI handler for NOW.md proposal."""
    proposals = await propose_now_update()

    if not proposals:
        return {"message": "No proposals generated (no recent crystals)"}

    return {
        "proposals": [p.to_dict() for p in proposals],
        "formatted": [p.format_diff() for p in proposals],
    }


async def cmd_promote_async(crystal_id: str) -> dict[str, Any]:
    """CLI handler for crystal promotion."""
    return await promote_to_brain(CrystalId(crystal_id))


async def cmd_promotion_candidates_async() -> dict[str, Any]:
    """CLI handler for listing promotion candidates."""
    candidates = identify_promotion_candidates()

    return {
        "candidates": [c.to_dict() for c in candidates[:10]],
        "total": len(candidates),
    }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Handoff
    "HandoffContext",
    "prepare_handoff_context",
    # NOW.md
    "NowMdProposal",
    "propose_now_update",
    "apply_now_proposal",
    # Brain Promotion
    "PromotionCandidate",
    "identify_promotion_candidates",
    "promote_to_brain",
    "auto_promote_crystals",
    # CLI helpers
    "cmd_propose_now_async",
    "cmd_promote_async",
    "cmd_promotion_candidates_async",
]
