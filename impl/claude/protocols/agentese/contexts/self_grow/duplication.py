"""
self.grow Duplication Detection

Similarity-based duplication checking to prevent creating
holons that already exist or are too similar to existing ones.

Uses:
1. Name similarity (Levenshtein distance)
2. Affordance overlap (Jaccard similarity)
3. Semantic embedding similarity (optional, if available)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .schemas import DuplicationCheckResult, HolonProposal

if TYPE_CHECKING:
    from ...logos import Logos


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute Levenshtein distance between two strings.

    Classic dynamic programming implementation.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Compute Levenshtein similarity (0.0 to 1.0).

    1.0 = identical, 0.0 = completely different
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return 1.0 - (distance / max_len)


def jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """
    Compute Jaccard similarity between two sets.

    1.0 = identical, 0.0 = no overlap
    """
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def compute_affordance_similarity(
    proposal_affordances: dict[str, list[str]],
    existing_affordances: set[str],
) -> float:
    """
    Compute affordance similarity between proposal and existing holon.

    Uses Jaccard similarity on the set of all verbs.
    """
    proposed_verbs = set(sum(proposal_affordances.values(), []))
    return jaccard_similarity(proposed_verbs, existing_affordances)


def compute_combined_similarity(
    name_sim: float,
    affordance_sim: float,
    name_weight: float = 0.4,
    affordance_weight: float = 0.6,
) -> float:
    """
    Compute weighted combined similarity.

    Default weights favor affordance similarity as more meaningful
    for determining duplication.
    """
    return (name_sim * name_weight) + (affordance_sim * affordance_weight)


async def check_duplication(
    proposal: HolonProposal,
    logos: "Logos | None" = None,
    existing_handles: list[str] | None = None,
    existing_affordances: dict[str, set[str]] | None = None,
) -> DuplicationCheckResult:
    """
    Check for existing similar holons.

    Args:
        proposal: The holon proposal to check
        logos: Optional Logos instance for registry lookup
        existing_handles: Optional list of existing handles (for testing)
        existing_affordances: Optional dict of handle -> affordances (for testing)

    Returns:
        DuplicationCheckResult with similarity info and recommendation
    """
    handle = f"{proposal.context}.{proposal.entity}"
    similar_holons: list[tuple[str, float]] = []

    # Get existing holons
    if existing_handles is None:
        existing_handles = []
        if logos is not None:
            try:
                result = await logos.invoke(
                    "world.registry.list", None, context=proposal.context
                )
                if isinstance(result, list):
                    existing_handles = result
            except Exception:
                pass  # No registry available

    if existing_affordances is None:
        existing_affordances = {}

    # Compare against each existing holon
    for existing_handle in existing_handles:
        if existing_handle == handle:
            continue  # Skip self

        # Extract entity name for comparison
        parts = existing_handle.split(".")
        existing_entity = parts[-1] if parts else existing_handle

        # Name similarity
        name_sim = levenshtein_similarity(proposal.entity, existing_entity)

        # Affordance similarity
        existing_affs = existing_affordances.get(existing_handle, set())
        if not existing_affs and logos is not None:
            # Try to get affordances from logos
            try:
                node = logos.resolve(existing_handle)
                if hasattr(node, "affordances"):
                    from ...node import AgentMeta

                    existing_affs = set(
                        node.affordances(AgentMeta(name="checker", archetype="default"))
                    )
            except Exception:
                existing_affs = set()

        aff_sim = compute_affordance_similarity(proposal.affordances, existing_affs)

        # Combined similarity
        combined_sim = compute_combined_similarity(name_sim, aff_sim)

        # Track if above threshold
        if combined_sim > 0.5:
            similar_holons.append((existing_handle, combined_sim))

    # Sort by similarity (highest first)
    similar_holons.sort(key=lambda x: x[1], reverse=True)

    # Determine recommendation
    highest_similarity = similar_holons[0][1] if similar_holons else 0.0

    if highest_similarity >= 0.9:
        recommendation = "reject"
        is_duplicate = True
    elif highest_similarity >= 0.7:
        recommendation = "merge"
        is_duplicate = True
    else:
        recommendation = "proceed"
        is_duplicate = False

    return DuplicationCheckResult(
        is_duplicate=is_duplicate,
        similar_holons=similar_holons[:5],  # Top 5
        highest_similarity=highest_similarity,
        recommendation=recommendation,  # type: ignore[arg-type]
    )


def check_duplication_sync(
    proposal: HolonProposal,
    existing_handles: list[str],
    existing_affordances: dict[str, set[str]] | None = None,
) -> DuplicationCheckResult:
    """
    Synchronous version of check_duplication for testing.

    Args:
        proposal: The holon proposal to check
        existing_handles: List of existing handles
        existing_affordances: Optional dict of handle -> affordances

    Returns:
        DuplicationCheckResult with similarity info and recommendation
    """
    import asyncio

    # Use asyncio.run for sync wrapper
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're already in an async context
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    check_duplication(
                        proposal,
                        logos=None,
                        existing_handles=existing_handles,
                        existing_affordances=existing_affordances,
                    ),
                )
                return future.result()
        else:
            return loop.run_until_complete(
                check_duplication(
                    proposal,
                    logos=None,
                    existing_handles=existing_handles,
                    existing_affordances=existing_affordances,
                )
            )
    except RuntimeError:
        return asyncio.run(
            check_duplication(
                proposal,
                logos=None,
                existing_handles=existing_handles,
                existing_affordances=existing_affordances,
            )
        )
