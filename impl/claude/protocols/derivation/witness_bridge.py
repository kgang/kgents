"""
Witness Bridge: Connect Derivation Framework to Witness Primitives.

Phase 3 of the Derivation Framework: Bridge witness marks, walks, and denials
to derivation updates.

The bridge answers: "How do witness observations update derivation confidence?"

Key Insight (from spec fusion):
    "Derivation IS identity, not metadata."

    When a Mark is emitted, it's evidence that agents were used.
    This stigmergic evidence accumulates over time, strengthening
    the derivation confidence of well-used agents.

Integration Points:
    Mark -> stigmergic_confidence (each mark increments usage)
    DifferentialDenial -> principle_draws decay (challenges weaken confidence)
    Walk -> aggregate updates (session-level batch processing)

Heritage:
    - Witness Primitives -> services/witness/mark.py
    - Derivation Framework -> spec/protocols/derivation-framework.md
    - Agent-as-Witness -> spec/heritage.md

Teaching:
    gotcha: Mark.origin contains the jewel/agent name, but it may be
            a Crown Jewel (like "brain") not a derivation-level agent.
            Use extract_agents_from_mark() to parse the origin field.

    gotcha: DifferentialDenial is a conceptual type - it represents
            a proof being challenged. The actual type may vary based
            on where the challenge originates (ASHC, human, other agent).

    gotcha: Walk updates are BATCH operations. Don't call them for every
            mark - call once at walk completion or periodically.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .registry import DerivationRegistry, get_registry
from .types import EvidenceType, PrincipleDraw

if TYPE_CHECKING:
    from services.witness.mark import Mark
    from services.witness.walk import Walk

logger = logging.getLogger("kgents.derivation.witness_bridge")


# =============================================================================
# DifferentialDenial: Conceptual Type for Challenges
# =============================================================================


@dataclass(frozen=True)
class DifferentialDenial:
    """
    A challenge to an agent's derivation.

    When evidence suggests an agent's behavior doesn't match its derivation,
    a DifferentialDenial is recorded. This weakens the relevant principle draws.

    The term "differential" captures that this is not a total rejection but
    a localized challenge to specific principles in specific contexts.

    Fields:
        original_trace_id: The mark that was challenged
        challenged_principle: Which principle failed (e.g., "Composable")
        challenge_evidence: Why it was challenged
        severity: 0.0-1.0, how severe the challenge is
        challenger: Who/what issued the challenge
        timestamp: When the challenge was recorded

    Example:
        >>> denial = DifferentialDenial(
        ...     original_trace_id="mark-abc123",
        ...     challenged_principle="Composable",
        ...     challenge_evidence="Pipeline failed due to incompatible types",
        ...     severity=0.3,  # Moderate severity
        ...     challenger="ashc",
        ... )
    """

    original_trace_id: str
    challenged_principle: str
    challenge_evidence: str
    severity: float = 0.2  # Default: light challenge
    challenger: str = "system"  # ashc, human, or agent name
    timestamp: datetime = None  # type: ignore

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc))

        # Clamp severity to [0.0, 1.0]
        if not 0.0 <= self.severity <= 1.0:
            object.__setattr__(
                self, "severity", max(0.0, min(1.0, self.severity))
            )


# =============================================================================
# Agent Extraction from Marks
# =============================================================================


def extract_agents_from_mark(mark: Mark) -> tuple[str, ...]:
    """
    Extract agent names from a Mark.

    The origin field typically contains the jewel or agent name that emitted
    the mark. This function extracts derivation-level agent names.

    Mapping:
        "witness" -> ("Witness",)
        "brain" -> ("Brain",)
        "logos" -> ("AGENTESE", "Logos")
        "town" -> ("Town",)
        "k-gent" -> ("K-gent",)

    Args:
        mark: The witness Mark to analyze

    Returns:
        Tuple of agent names that have derivations

    Teaching:
        gotcha: Crown Jewel names are lowercase in marks but titlecase
                in derivations. This function handles the mapping.
    """
    origin = mark.origin.lower()

    # Map origin to derivation agent names
    ORIGIN_TO_AGENTS: dict[str, tuple[str, ...]] = {
        "witness": ("Witness",),
        "brain": ("Brain",),
        "logos": ("Logos",),
        "town": ("Town",),
        "park": ("Park",),
        "forge": ("Forge",),
        "conductor": ("Conductor",),
        "gardener": ("Gardener",),
        "liminal": ("Liminal",),
        "gestalt": ("Gestalt",),
        "k-gent": ("K-gent",),
        "m-gent": ("M-gent",),
        # Flux agents
        "flux": ("Flux",),
        # Bootstrap agents (rarely in marks, but handle them)
        "id": ("Id",),
        "compose": ("Compose",),
        "judge": ("Judge",),
        "ground": ("Ground",),
        "contradict": ("Contradict",),
        "sublate": ("Sublate",),
        "fix": ("Fix",),
    }

    # Direct lookup
    if origin in ORIGIN_TO_AGENTS:
        return ORIGIN_TO_AGENTS[origin]

    # Check for partial matches (e.g., "brain_crystal" -> "Brain")
    for key, agents in ORIGIN_TO_AGENTS.items():
        if key in origin:
            return agents

    # Unknown origin - return as-is with titlecase
    return (origin.title(),)


# =============================================================================
# Mark -> Stigmergic Update
# =============================================================================


async def mark_updates_stigmergy(
    mark: Mark,
    registry: DerivationRegistry | None = None,
) -> dict[str, int]:
    """
    Update stigmergic confidence based on a Mark.

    When an action is witnessed, update stigmergic confidence for the
    agents involved. Successful marks reinforce; this is pure usage tracking.

    Flow:
        1. Extract agents from mark.origin
        2. For each agent with a derivation:
           a. Increment usage count
           b. Registry handles stigmergic confidence updates (every 10 uses)
        3. Return usage counts

    Args:
        mark: The witness Mark to process
        registry: Derivation registry (uses global if not provided)

    Returns:
        Dict of agent_name -> new_usage_count

    Teaching:
        gotcha: This function is async for consistency with other bridge
                functions, even though current impl is sync. Future versions
                may need async for distributed stigmergy.
    """
    if registry is None:
        registry = get_registry()

    agents = extract_agents_from_mark(mark)
    usage_counts: dict[str, int] = {}

    for agent_name in agents:
        # Check if agent has a derivation
        if not registry.exists(agent_name):
            logger.debug(f"No derivation for agent '{agent_name}', skipping stigmergy update")
            continue

        # Increment usage (registry handles confidence updates internally)
        new_count = registry.increment_usage(agent_name)
        usage_counts[agent_name] = new_count

        logger.debug(f"Mark {mark.id}: {agent_name} usage count -> {new_count}")

    return usage_counts


# =============================================================================
# DifferentialDenial -> Derivation Weakening
# =============================================================================


async def denial_weakens_derivation(
    denial: DifferentialDenial,
    registry: DerivationRegistry | None = None,
    agent_name: str | None = None,
) -> list[str]:
    """
    Weaken derivation when a proof is challenged.

    Differential denials are learning opportunities. When an agent's behavior
    doesn't match its claimed principles, the relevant principle draws decay.

    Flow:
        1. Find affected agents (from trace or explicit agent_name)
        2. For each affected agent:
           a. Find the principle draw that was challenged
           b. Decay draw_strength by severity factor
           c. Propagate confidence changes through DAG
        3. Return list of affected agent names

    Args:
        denial: The challenge to process
        registry: Derivation registry (uses global if not provided)
        agent_name: Explicit agent name (overrides trace lookup)

    Returns:
        List of agent names whose derivations were weakened

    Teaching:
        gotcha: Categorical evidence is NEVER weakened by denials.
                If a principle has categorical evidence, the denial is logged
                but the draw_strength remains 1.0. This is by design:
                if the categorical proof is wrong, the proof was never valid.
    """
    if registry is None:
        registry = get_registry()

    affected: list[str] = []

    # Determine which agents to update
    if agent_name:
        agent_names = [agent_name]
    else:
        # In a real implementation, we'd look up the trace and find agents
        # For now, log and return empty
        logger.warning(
            f"DifferentialDenial for trace {denial.original_trace_id} "
            f"without explicit agent_name - cannot determine affected agents"
        )
        return affected

    for name in agent_names:
        derivation = registry.get(name)
        if derivation is None:
            logger.warning(f"No derivation for agent '{name}', skipping denial")
            continue

        # Find and decay the challenged principle
        new_draws: list[PrincipleDraw] = []
        was_weakened = False

        for draw in derivation.principle_draws:
            if draw.principle == denial.challenged_principle:
                # Categorical evidence is never weakened
                if draw.evidence_type == EvidenceType.CATEGORICAL:
                    logger.info(
                        f"Denial of categorical evidence for {name}.{draw.principle} "
                        f"ignored - categorical proofs are indefeasible"
                    )
                    new_draws.append(draw)
                    continue

                # Decay by severity factor
                decay_factor = 1.0 - denial.severity
                new_strength = max(0.1, draw.draw_strength * decay_factor)

                new_draw = replace(
                    draw,
                    draw_strength=new_strength,
                    last_verified=denial.timestamp,
                )
                new_draws.append(new_draw)
                was_weakened = True

                logger.info(
                    f"DifferentialDenial: {name}.{draw.principle} "
                    f"{draw.draw_strength:.2f} -> {new_strength:.2f}"
                )
            else:
                new_draws.append(draw)

        if was_weakened:
            # Update derivation with weakened draws
            updated = replace(derivation, principle_draws=tuple(new_draws))
            registry._derivations[name] = updated
            registry._propagate_confidence(name)
            affected.append(name)

    return affected


# =============================================================================
# Walk -> Aggregate Derivation Updates
# =============================================================================


async def walk_updates_derivations(
    walk: Walk,
    mark_store: object | None = None,  # MarkStore from witness
    registry: DerivationRegistry | None = None,
) -> dict[str, dict[str, int | float]]:
    """
    Aggregate derivation updates from a Walk.

    A Walk is a session-level abstraction. When a Walk completes (or periodically
    during long walks), we batch update derivations for all marks in the walk.

    This is more efficient than updating per-mark because:
        - Confidence propagation happens once per agent, not per mark
        - Usage counts can be batched
        - Walk-level statistics can inform updates

    Flow:
        1. Collect all marks in the walk
        2. Aggregate usage counts per agent
        3. Batch update usage counts
        4. Record walk-level metadata in derivations
        5. Return summary of updates

    Args:
        walk: The Walk to process
        mark_store: Optional MarkStore to retrieve marks (uses walk.mark_ids if None)
        registry: Derivation registry (uses global if not provided)

    Returns:
        Dict of agent_name -> {"usage_before": int, "usage_after": int, "marks": int}

    Teaching:
        gotcha: This function takes a walk, not mark_store.get_walk_traces().
                The walk.mark_ids provides the trace IDs directly.

        gotcha: Calling this repeatedly on the same walk is safe but wasteful.
                Use walk.metadata["derivation_updated"] to track.
    """
    if registry is None:
        registry = get_registry()

    # Aggregate usage counts per agent
    agent_marks: dict[str, int] = {}

    # Process mark IDs from the walk
    # Note: In a full implementation, we'd load actual marks from mark_store
    # For now, we simulate based on walk metadata
    for mark_id in walk.mark_ids:
        # Without the actual mark, we can't determine agents
        # This is a limitation - in practice, you'd pass the mark_store
        # and load each mark to get its origin
        pass

    # If we have mark_store, use it to get actual marks
    if mark_store is not None and hasattr(mark_store, "get"):
        for mark_id in walk.mark_ids:
            mark = mark_store.get(mark_id)
            if mark is None:
                continue

            agents = extract_agents_from_mark(mark)
            for agent in agents:
                agent_marks[agent] = agent_marks.get(agent, 0) + 1
    else:
        # Fallback: Extract from walk participants if available
        for participant in walk.participants:
            # Participant names might map to agents
            agents = _participant_to_agents(participant)
            for agent in agents:
                # Count as one mark per participant (rough estimate)
                agent_marks[agent] = agent_marks.get(agent, 0) + 1

    # Batch update usage counts
    results: dict[str, dict[str, int | float]] = {}

    for agent_name, mark_count in agent_marks.items():
        if not registry.exists(agent_name):
            continue

        before = registry.get_usage_count(agent_name)

        # Increment by mark count
        for _ in range(mark_count):
            registry.increment_usage(agent_name)

        after = registry.get_usage_count(agent_name)

        derivation = registry.get(agent_name)
        results[agent_name] = {
            "usage_before": before,
            "usage_after": after,
            "marks": mark_count,
            "confidence": derivation.total_confidence if derivation else 0.0,
        }

        logger.info(
            f"Walk {walk.id}: {agent_name} usage {before} -> {after} "
            f"({mark_count} marks)"
        )

    return results


def _participant_to_agents(participant: object) -> tuple[str, ...]:
    """
    Map a Walk participant to derivation agent names.

    Participants are humans or agents in a Walk. This maps their names
    to derivation-level agent names.
    """
    name = getattr(participant, "name", "").lower()

    # Known agent mappings
    PARTICIPANT_TO_AGENTS: dict[str, tuple[str, ...]] = {
        "witness": ("Witness",),
        "brain": ("Brain",),
        "claude": ("K-gent",),  # Claude sessions use K-gent
        "kent": (),  # Humans don't have derivations
    }

    if name in PARTICIPANT_TO_AGENTS:
        return PARTICIPANT_TO_AGENTS[name]

    # Check if participant is an agent (not human)
    role = getattr(participant, "role", "")
    if role == "contributor" or "agent" in role.lower():
        return (name.title(),)

    return ()


# =============================================================================
# Convenience: Process All Witness Events
# =============================================================================


async def sync_witness_to_derivations(
    marks: list[Mark],
    denials: list[DifferentialDenial] | None = None,
    registry: DerivationRegistry | None = None,
) -> dict[str, Any]:
    """
    Batch sync multiple witness events to derivations.

    Convenience function for processing a batch of marks and denials.
    More efficient than calling individual functions.

    Args:
        marks: List of Marks to process
        denials: Optional list of DifferentialDenials
        registry: Derivation registry (uses global if not provided)

    Returns:
        Summary dict with usage updates and weakened derivations
    """
    if registry is None:
        registry = get_registry()

    usage_updates: dict[str, int] = {}
    weakened_agents: list[str] = []
    marks_processed = 0
    denials_processed = 0

    # Process marks
    for mark in marks:
        usage = await mark_updates_stigmergy(mark, registry)
        for agent, count in usage.items():
            usage_updates[agent] = count  # Latest count
        marks_processed += 1

    # Process denials
    if denials:
        for denial in denials:
            weakened = await denial_weakens_derivation(denial, registry)
            weakened_agents.extend(weakened)
            denials_processed += 1

    return {
        "marks_processed": marks_processed,
        "usage_updates": usage_updates,
        "denials_processed": denials_processed,
        "weakened_agents": weakened_agents,
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "DifferentialDenial",
    # Core functions
    "extract_agents_from_mark",
    "mark_updates_stigmergy",
    "denial_weakens_derivation",
    "walk_updates_derivations",
    # Convenience
    "sync_witness_to_derivations",
]
