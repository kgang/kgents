"""
Constitutional Reward System for Chat.

Backward-compatible wrapper around generalized constitutional scoring.

Philosophy:
    "Every turn is evaluated. Every action is justified. Every score is witnessed."

See: spec/protocols/chat-unified.md §1.2, §4.2
See: spec/principles/CONSTITUTION.md
See: services/constitutional/reward.py (generalized implementation)

Teaching:
    gotcha: This module is now a thin wrapper for backward compatibility.
            The actual implementation lives in services/constitutional/reward.py.
            We re-export Principle and PrincipleScore from the generalized module.
            (Evidence: Import from services.constitutional)
"""

from __future__ import annotations

from services.chat.evidence import TurnResult

# Import from generalized constitutional module
from services.constitutional import (
    Principle,
    PrincipleScore,
    constitutional_reward as _constitutional_reward,
)

# =============================================================================
# Re-export Generalized Types
# =============================================================================

# These are re-exported from services.constitutional for backward compatibility
# Principle = Enum with 7 constitutional values
# PrincipleScore = Dataclass with scoring methods


# =============================================================================
# Constitutional Reward Function (Chat-Specific Wrapper)
# =============================================================================


def constitutional_reward(
    action: str,
    turn_result: TurnResult | None = None,
    has_mutations: bool = False,
) -> PrincipleScore:
    """
    Compute Constitutional reward for a chat action.

    This is a backward-compatible wrapper around the generalized constitutional_reward
    function in services.constitutional.reward.

    Evaluates the action against the 7 Constitutional principles:
    1. Tasteful: Does this serve a clear purpose?
    2. Curated: Is this intentional?
    3. Ethical: Does this respect human agency?
    4. Joy-Inducing: Does this delight?
    5. Composable: Does this compose cleanly?
    6. Heterarchical: Can this both lead and follow?
    7. Generative: Is this compressive?

    Scoring rules (from spec/protocols/chat-unified.md §4.2):
    - ETHICAL: Lower if mutations occur but aren't acknowledged
    - COMPOSABLE: Lower if too many tools used (>5)
    - JOY_INDUCING: Lower for very short responses (<20 chars)
    - GENERATIVE: Lower if context utilization >90%
    - TASTEFUL, CURATED, HETERARCHICAL: Default 1.0 (override for specific cases)

    Args:
        action: The action being evaluated (e.g., "send_message", "fork")
        turn_result: Optional result of the turn (for tool/content analysis)
        has_mutations: True if mutations occurred in this turn

    Returns:
        PrincipleScore with all 7 principles evaluated

    Examples:
        >>> # Perfect turn
        >>> result = TurnResult(response="Great!", tools=[])
        >>> score = constitutional_reward("send_message", result)
        >>> score.ethical
        1.0

        >>> # Turn with unacknowledged mutations
        >>> score = constitutional_reward("send_message", has_mutations=True)
        >>> score.ethical < 1.0
        True

        >>> # Turn with too many tools
        >>> result = TurnResult(tools=[{"name": f"tool_{i}"} for i in range(10)])
        >>> score = constitutional_reward("send_message", result)
        >>> score.composable < 1.0
        True
    """
    # Build context dict for generalized function
    context = {
        "turn_result": turn_result,
        "has_mutations": has_mutations,
    }

    # Delegate to generalized constitutional_reward
    return _constitutional_reward(action, context, domain="chat")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Principle",
    "PrincipleScore",
    "constitutional_reward",
]
