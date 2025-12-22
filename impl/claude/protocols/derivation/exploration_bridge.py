"""
Phase 6: Exploration Harness → Derivation Bridge.

Trails ARE evidence. This module bridges exploration trails to derivation
principle draws, converting behavioral evidence into confidence updates.

The core insight: exploration patterns reveal principle instantiation:
- Long, diverse edges → Composable
- Avoids loops → Generative
- Depth before breadth → Curated
- Committed claims → Ethical
- Backtrack recovery → Heterarchical

Law 6.1 (Trail Evidence Additivity):
    Trails can only strengthen principle draws, never weaken.
    Negative evidence comes via Witness denials.

See: spec/protocols/derivation-framework.md §6.1
See: spec/protocols/exploration-harness.md

Teaching:
    gotcha: Trails are *behavioral* evidence—they show what the agent actually did,
            not what it claimed. This is EvidenceType.EMPIRICAL.
            (Evidence: test_exploration_bridge.py::test_trails_are_empirical)

    gotcha: Bootstrap agents are immune to trail evidence updates.
            (Evidence: test_exploration_bridge.py::test_bootstrap_immune)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .types import Derivation, EvidenceType, PrincipleDraw

if TYPE_CHECKING:
    from protocols.exploration.types import Claim, CommitmentLevel, Trail

    from .registry import DerivationRegistry


# =============================================================================
# Trail Evidence Types
# =============================================================================


@dataclass(frozen=True)
class TrailEvidence:
    """
    Bridge between exploration trails and derivation updates.

    Trails are *behavioral* evidence—they show what the agent actually did,
    not what it claimed. This is EvidenceType.EMPIRICAL.

    Teaching:
        gotcha: principles_signaled is a tuple of (principle, strength) pairs.
                The strength is computed from trail patterns, not claimed.
    """

    trail_id: str
    agent_name: str
    principles_signaled: tuple[tuple[str, float], ...]  # (principle, strength)
    commitment_level: str  # "tentative" | "moderate" | "strong" | "definitive"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_trail(
        cls,
        trail: "Trail",
        claim: "Claim",
        agent_name: str,
    ) -> "TrailEvidence":
        """
        Extract derivation evidence from an exploration trail.

        Pattern analysis:
        - Long trails with diverse edge types → Composable (0.5-0.9)
        - Trails that avoid loops → Generative (0.8)
        - Depth before breadth → Curated (0.5-0.7)
        - Committed claims → Ethical (0.7-0.9)
        - Backtrack recovery → Heterarchical (0.6)
        """
        principles: list[tuple[str, float]] = []

        steps = trail.steps
        edges = trail.edges_followed if hasattr(trail, "edges_followed") else []

        # Pattern 1: Long trails with diverse edge types → Composable
        if len(steps) > 5:
            unique_edges = len(set(edges)) if edges else 0
            edge_diversity = unique_edges / len(steps) if steps else 0
            if edge_diversity > 0.3:
                strength = min(0.9, 0.5 + edge_diversity * 0.4)
                principles.append(("Composable", strength))

        # Pattern 2: Trails that avoid loops → Generative
        visited: set[str] = set()
        revisits = 0
        for step in steps:
            node = step.node if hasattr(step, "node") else str(step)
            if node in visited:
                revisits += 1
            visited.add(node)

        if revisits == 0 and len(steps) > 3:
            principles.append(("Generative", 0.8))

        # Pattern 3: Committed claims → Ethical
        commitment_level = claim.commitment_level
        if commitment_level is None:
            commitment = "tentative"
        elif hasattr(commitment_level, "value"):
            commitment = commitment_level.value
        else:
            commitment = str(commitment_level)
        if commitment == "definitive":
            principles.append(("Ethical", 0.9))
        elif commitment == "strong":
            principles.append(("Ethical", 0.8))
        elif commitment == "moderate":
            principles.append(("Ethical", 0.7))

        # Pattern 4: Backtrack recovery (if trail has annotations about backtrack)
        if hasattr(trail, "annotations") and trail.annotations:
            for annotation in trail.annotations.values():
                if "backtrack" in annotation.lower() or "recover" in annotation.lower():
                    principles.append(("Heterarchical", 0.6))
                    break

        return cls(
            trail_id=trail.id,
            agent_name=agent_name,
            principles_signaled=tuple(principles),
            commitment_level=commitment,
        )


# =============================================================================
# Bridge Functions
# =============================================================================


def apply_trail_evidence(
    evidence: TrailEvidence,
    registry: "DerivationRegistry",
) -> Derivation | None:
    """
    Apply trail evidence to derivation.

    Law 6.1 (Trail Evidence Additivity):
        Trails can only increase principle draw strength, not decrease.
        This reflects "evidence accumulates" from ASHC.

    Args:
        evidence: The trail evidence to apply
        registry: The derivation registry

    Returns:
        Updated derivation, or None if agent not found

    Teaching:
        gotcha: Bootstrap agents are immune—their confidence never changes.
    """
    if not registry.exists(evidence.agent_name):
        return None

    derivation = registry.get(evidence.agent_name)
    if derivation is None:
        return None

    if derivation.is_bootstrap:
        return derivation  # Bootstrap agents don't change

    # Merge principle draws, only increasing strength (Law 6.1)
    existing_draws = {d.principle: d for d in derivation.principle_draws}

    for principle, strength in evidence.principles_signaled:
        if principle in existing_draws:
            existing = existing_draws[principle]
            if strength > existing.draw_strength:
                # Strengthen existing draw
                new_sources = existing.evidence_sources + (f"trail:{evidence.trail_id}",)
                existing_draws[principle] = replace(
                    existing,
                    draw_strength=strength,
                    evidence_sources=new_sources,
                    last_verified=datetime.now(timezone.utc),
                )
        else:
            # Create new draw
            existing_draws[principle] = PrincipleDraw(
                principle=principle,
                draw_strength=strength,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=(f"trail:{evidence.trail_id}",),
            )

    # Update derivation
    updated = derivation.with_principle_draws(tuple(existing_draws.values()))
    registry._derivations[evidence.agent_name] = updated
    registry._propagate_confidence(evidence.agent_name)

    return updated


async def apply_trail_evidence_async(
    evidence: TrailEvidence,
    registry: "DerivationRegistry",
) -> Derivation | None:
    """
    Async version of apply_trail_evidence.

    For use in async contexts (e.g., ExplorationHarness.commit()).
    """
    return apply_trail_evidence(evidence, registry)


def trail_to_derivation_evidence(
    trail: "Trail",
    claim: "Claim",
    agent_name: str,
) -> TrailEvidence:
    """
    Convert an exploration trail to derivation evidence.

    Convenience function that wraps TrailEvidence.from_trail().
    """
    return TrailEvidence.from_trail(trail, claim, agent_name)


def merge_trail_evidence(
    evidences: list[TrailEvidence],
) -> TrailEvidence:
    """
    Merge multiple trail evidences into one.

    Uses max strength for each principle (Law 6.1 additivity).
    """
    if not evidences:
        raise ValueError("Cannot merge empty evidence list")

    # Take metadata from first evidence
    first = evidences[0]

    # Merge principles, keeping max strength
    principle_strengths: dict[str, float] = {}
    for evidence in evidences:
        for principle, strength in evidence.principles_signaled:
            current = principle_strengths.get(principle, 0.0)
            principle_strengths[principle] = max(current, strength)

    return TrailEvidence(
        trail_id=f"merged:{first.trail_id}",
        agent_name=first.agent_name,
        principles_signaled=tuple(principle_strengths.items()),
        commitment_level=first.commitment_level,
    )


def batch_apply_trail_evidence(
    evidences: list[TrailEvidence],
    registry: "DerivationRegistry",
) -> dict[str, Derivation | None]:
    """
    Apply multiple trail evidences in batch.

    More efficient than calling apply_trail_evidence() for each.
    Propagation happens once at the end.

    Returns:
        Dict mapping agent_name → updated derivation (or None)
    """
    results: dict[str, Derivation | None] = {}
    affected_agents: set[str] = set()

    for evidence in evidences:
        if not registry.exists(evidence.agent_name):
            results[evidence.agent_name] = None
            continue

        derivation = registry.get(evidence.agent_name)
        if derivation is None or derivation.is_bootstrap:
            results[evidence.agent_name] = derivation
            continue

        # Merge without propagation
        existing_draws = {d.principle: d for d in derivation.principle_draws}

        for principle, strength in evidence.principles_signaled:
            if principle in existing_draws:
                existing = existing_draws[principle]
                if strength > existing.draw_strength:
                    new_sources = existing.evidence_sources + (f"trail:{evidence.trail_id}",)
                    existing_draws[principle] = replace(
                        existing,
                        draw_strength=strength,
                        evidence_sources=new_sources,
                        last_verified=datetime.now(timezone.utc),
                    )
            else:
                existing_draws[principle] = PrincipleDraw(
                    principle=principle,
                    draw_strength=strength,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=(f"trail:{evidence.trail_id}",),
                )

        updated = derivation.with_principle_draws(tuple(existing_draws.values()))
        registry._derivations[evidence.agent_name] = updated
        results[evidence.agent_name] = updated
        affected_agents.add(evidence.agent_name)

    # Propagate once for all affected agents
    for agent_name in affected_agents:
        registry._propagate_confidence(agent_name)

    return results


__all__ = [
    "TrailEvidence",
    "apply_trail_evidence",
    "apply_trail_evidence_async",
    "trail_to_derivation_evidence",
    "merge_trail_evidence",
    "batch_apply_trail_evidence",
]
