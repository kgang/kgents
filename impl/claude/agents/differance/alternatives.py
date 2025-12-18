"""
Static Alternative Registry for Crown Jewels.

Per plans/differance-crown-jewel-wiring.md (Decision 3):
- Tier 1: Static alternatives (always available, zero cost)
- Tier 2: Dynamic alternatives (computed on demand, lazy)

This module provides Tier 1 static alternatives for each Crown Jewel.

Usage:
    from agents.differance.alternatives import get_alternatives

    alternatives = get_alternatives("brain", "capture")
    # Returns list of Alternative objects

See: spec/protocols/differance.md
See: plans/differance-crown-jewel-wiring.md (Phase 6B, 6C)
"""

from __future__ import annotations

from .trace import Alternative

# =============================================================================
# Brain Alternatives (Phase 6B)
# =============================================================================

BRAIN_ALTERNATIVES: dict[str, list[Alternative]] = {
    "capture": [
        Alternative(
            operation="auto_tag",
            inputs=(),
            reason_rejected="User didn't request auto-tagging",
            could_revisit=True,
        ),
        Alternative(
            operation="defer_embedding",
            inputs=(),
            reason_rejected="Immediate embedding preferred for search",
            could_revisit=True,
        ),
    ],
    "surface": [
        Alternative(
            operation="different_seed",
            inputs=(),
            reason_rejected="Used current entropy seed",
            could_revisit=True,
        ),
        Alternative(
            operation="context_weighted",
            inputs=(),
            reason_rejected="No context provided, using random",
            could_revisit=True,
        ),
    ],
    "delete": [
        Alternative(
            operation="archive_instead",
            inputs=(),
            reason_rejected="Permanent deletion requested",
            could_revisit=False,
        ),
        Alternative(
            operation="soft_delete",
            inputs=(),
            reason_rejected="Hard delete preferred",
            could_revisit=False,
        ),
    ],
}

# =============================================================================
# Gardener Alternatives (Phase 6C)
# =============================================================================

GARDENER_ALTERNATIVES: dict[str, list[Alternative]] = {
    "plant": [
        Alternative(
            operation="different_lifecycle",
            inputs=("seed",),
            reason_rejected="Default lifecycle used",
            could_revisit=True,
        ),
        Alternative(
            operation="auto_connect",
            inputs=(),
            reason_rejected="No similar ideas found to connect",
            could_revisit=True,
        ),
    ],
    "nurture": [
        Alternative(
            operation="prune",
            inputs=(),
            reason_rejected="Nurturing chosen over pruning",
            could_revisit=True,
        ),
        Alternative(
            operation="water",
            inputs=(),
            reason_rejected="Different tending verb selected",
            could_revisit=True,
        ),
    ],
    "harvest": [
        Alternative(
            operation="stay",
            inputs=(),
            reason_rejected="Promotion requested",
            could_revisit=False,
        ),
        Alternative(
            operation="compost",
            inputs=(),
            reason_rejected="Idea is viable, harvest not compost",
            could_revisit=True,
        ),
    ],
    "session_start": [
        Alternative(
            operation="resume_previous",
            inputs=(),
            reason_rejected="New session requested",
            could_revisit=True,
        ),
    ],
    "session_end": [
        Alternative(
            operation="extend",
            inputs=(),
            reason_rejected="Session concluded",
            could_revisit=False,
        ),
    ],
    "create_plot": [
        Alternative(
            operation="use_existing",
            inputs=(),
            reason_rejected="New plot requested",
            could_revisit=True,
        ),
    ],
}

# =============================================================================
# Town Alternatives (Future)
# =============================================================================

TOWN_ALTERNATIVES: dict[str, list[Alternative]] = {
    "dialogue_turn": [
        Alternative(
            operation="silent",
            inputs=(),
            reason_rejected="Citizen chose to speak",
            could_revisit=True,
        ),
        Alternative(
            operation="different_topic",
            inputs=(),
            reason_rejected="Topic was relevant to context",
            could_revisit=True,
        ),
    ],
}

# =============================================================================
# Atelier Alternatives (Future)
# =============================================================================

ATELIER_ALTERNATIVES: dict[str, list[Alternative]] = {
    "submit_bid": [
        Alternative(
            operation="higher_bid",
            inputs=(),
            reason_rejected="Budget constraint",
            could_revisit=True,
        ),
        Alternative(
            operation="withdraw",
            inputs=(),
            reason_rejected="Piece is desired",
            could_revisit=True,
        ),
    ],
}

# =============================================================================
# Registry Access
# =============================================================================

_REGISTRIES: dict[str, dict[str, list[Alternative]]] = {
    "brain": BRAIN_ALTERNATIVES,
    "gardener": GARDENER_ALTERNATIVES,
    "town": TOWN_ALTERNATIVES,
    "atelier": ATELIER_ALTERNATIVES,
}


def get_alternatives(jewel: str, operation: str) -> list[Alternative]:
    """
    Get static alternatives for a Crown Jewel operation.

    Args:
        jewel: Crown Jewel name (brain, gardener, town, atelier)
        operation: Operation name (capture, plant, dialogue_turn, etc.)

    Returns:
        List of Alternative objects, empty if not found

    Example:
        >>> alts = get_alternatives("brain", "capture")
        >>> assert len(alts) == 2
        >>> assert alts[0].operation == "auto_tag"
    """
    registry = _REGISTRIES.get(jewel.lower(), {})
    return registry.get(operation, [])


def list_operations(jewel: str) -> list[str]:
    """List all operations with alternatives for a jewel."""
    registry = _REGISTRIES.get(jewel.lower(), {})
    return list(registry.keys())


def list_jewels() -> list[str]:
    """List all jewels with registered alternatives."""
    return list(_REGISTRIES.keys())


__all__ = [
    "Alternative",
    "BRAIN_ALTERNATIVES",
    "GARDENER_ALTERNATIVES",
    "TOWN_ALTERNATIVES",
    "ATELIER_ALTERNATIVES",
    "get_alternatives",
    "list_operations",
    "list_jewels",
]
