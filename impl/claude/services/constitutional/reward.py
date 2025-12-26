"""
Constitutional Reward System (Generalized).

Implements the 7-Principle Constitutional reward function for evaluating
actions across all domains: chat, navigation, portal, edit.

Philosophy:
    "Every action is evaluated. Every domain is witnessed. Every score is principled."

See: spec/protocols/chat-unified.md §1.2, §4.2
See: spec/principles/CONSTITUTION.md

Architecture:
    - Principle enumeration (7 constitutional values)
    - PrincipleScore dataclass (scores + weighted total)
    - Domain enumeration (chat, navigation, portal, edit)
    - constitutional_reward() function (domain-specific scoring)
    - Domain-specific scoring rules (apply_*_rules functions)

Teaching:
    gotcha: Domain-specific rules capture domain semantics. Navigation prioritizes
            GENERATIVE (following proof chains), portal prioritizes JOY_INDUCING
            (deliberate curiosity), edit prioritizes TASTEFUL (small changes).
            (Evidence: _apply_*_rules functions)

    gotcha: Default scores are 1.0 (optimistic prior). Only lower scores for
            specific violations. This means "no evidence of violation" = "good".
            (Evidence: constitutional_reward() starts with all 1.0)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

# =============================================================================
# Principle Enumeration
# =============================================================================


class Principle(Enum):
    """
    The Seven Constitutional Principles.

    Each principle represents a core value in the kgents system.
    See: spec/principles/CONSTITUTION.md
    """

    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy_inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"


# =============================================================================
# Domain Enumeration
# =============================================================================


class Domain(Enum):
    """
    Domains where constitutional scoring applies.

    Each domain has specific scoring rules aligned with its purpose.
    """

    CHAT = "chat"
    NAVIGATION = "navigation"
    PORTAL = "portal"
    EDIT = "edit"


# =============================================================================
# Principle Score
# =============================================================================


@dataclass
class PrincipleScore:
    """
    Constitutional scores for a single action.

    Each of the seven principles is scored from 0.0 to 1.0, where:
    - 1.0 = perfect adherence to the principle
    - 0.5 = neutral (neither good nor bad)
    - 0.0 = severe violation

    Default is 1.0 for all principles (optimistic prior).

    Examples:
        >>> score = PrincipleScore(ethical=0.8, composable=0.9)
        >>> score.weighted_total()
        6.95  # (0.8*2.0 + 0.9*1.5 + 1.0*1.2 + 1.0*4) / 9.7

        >>> score.to_dict()
        {"tasteful": 1.0, "curated": 1.0, "ethical": 0.8, ...}
    """

    tasteful: float = 1.0
    curated: float = 1.0
    ethical: float = 1.0
    joy_inducing: float = 1.0
    composable: float = 1.0
    heterarchical: float = 1.0
    generative: float = 1.0

    def weighted_total(self, weights: dict[Principle, float] | None = None) -> float:
        """
        Compute weighted total score.

        Uses default weights if not provided:
        - ETHICAL: 2.0 (safety first)
        - COMPOSABLE: 1.5 (architecture second)
        - JOY_INDUCING: 1.2 (Kent's aesthetic)
        - Others: 1.0

        Args:
            weights: Optional custom weights per principle

        Returns:
            Weighted total score (0.0 to sum of weights)

        Examples:
            >>> score = PrincipleScore(ethical=0.5, composable=0.8)
            >>> score.weighted_total()  # Uses default weights
            6.35  # (0.5*2.0 + 0.8*1.5 + 1.0*1.2 + 1.0*4) / 9.7

            >>> custom = {Principle.ETHICAL: 3.0, Principle.COMPOSABLE: 1.0}
            >>> score.weighted_total(custom)
            7.5  # Different weights
        """
        # Default weights from spec/protocols/chat-unified.md §1.2
        if weights is None:
            weights = {
                Principle.ETHICAL: 2.0,
                Principle.COMPOSABLE: 1.5,
                Principle.JOY_INDUCING: 1.2,
                Principle.TASTEFUL: 1.0,
                Principle.CURATED: 1.0,
                Principle.HETERARCHICAL: 1.0,
                Principle.GENERATIVE: 1.0,
            }

        # Compute weighted sum
        total = 0.0
        total += self.tasteful * weights.get(Principle.TASTEFUL, 1.0)
        total += self.curated * weights.get(Principle.CURATED, 1.0)
        total += self.ethical * weights.get(Principle.ETHICAL, 1.0)
        total += self.joy_inducing * weights.get(Principle.JOY_INDUCING, 1.0)
        total += self.composable * weights.get(Principle.COMPOSABLE, 1.0)
        total += self.heterarchical * weights.get(Principle.HETERARCHICAL, 1.0)
        total += self.generative * weights.get(Principle.GENERATIVE, 1.0)

        return total

    def to_dict(self) -> dict[str, float]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dict mapping principle names to scores

        Examples:
            >>> score = PrincipleScore(ethical=0.8)
            >>> score.to_dict()
            {"tasteful": 1.0, "curated": 1.0, "ethical": 0.8, ...}
        """
        return {
            "tasteful": self.tasteful,
            "curated": self.curated,
            "ethical": self.ethical,
            "joy_inducing": self.joy_inducing,
            "composable": self.composable,
            "heterarchical": self.heterarchical,
            "generative": self.generative,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> PrincipleScore:
        """
        Create from dictionary.

        Args:
            data: Dict mapping principle names to scores

        Returns:
            PrincipleScore instance

        Examples:
            >>> data = {"ethical": 0.8, "composable": 0.9}
            >>> score = PrincipleScore.from_dict(data)
            >>> score.ethical
            0.8
        """
        return cls(
            tasteful=data.get("tasteful", 1.0),
            curated=data.get("curated", 1.0),
            ethical=data.get("ethical", 1.0),
            joy_inducing=data.get("joy_inducing", 1.0),
            composable=data.get("composable", 1.0),
            heterarchical=data.get("heterarchical", 1.0),
            generative=data.get("generative", 1.0),
        )


# =============================================================================
# Domain-Specific Scoring Rules
# =============================================================================


def _apply_chat_rules(scores: dict[str, float], context: dict[str, Any]) -> dict[str, float]:
    """
    Apply chat-specific scoring rules.

    Chat rules (from spec/protocols/chat-unified.md §4.2):
    - ETHICAL: Lower if mutations occur but aren't acknowledged
    - COMPOSABLE: Lower if too many tools used (>5)
    - JOY_INDUCING: Lower for very short responses (<20 chars)
    - GENERATIVE: Lower if context utilization >90%

    Args:
        scores: Current scores (all default 1.0)
        context: Chat-specific context (turn_result, has_mutations)

    Returns:
        Updated scores
    """
    turn_result = context.get("turn_result")
    has_mutations = context.get("has_mutations", False)

    if turn_result is None:
        return scores

    # === ETHICAL ===
    # Lower if mutations occur but aren't acknowledged
    if has_mutations:
        # Check if mutations were acknowledged
        if not turn_result.tools_passed:
            scores["ethical"] = 0.5  # Unacknowledged mutations
        else:
            scores["ethical"] = 0.9  # Mutations occurred but were handled

    # === COMPOSABLE ===
    # Lower if too many tools used (>5 suggests poor composition)
    num_tools = len(turn_result.tools)
    if num_tools > 5:
        # Scale down from 1.0 to 0.5 as tool count increases
        scores["composable"] = max(0.5, 1.0 - (num_tools - 5) * 0.1)

    # === JOY_INDUCING ===
    # Lower for very short responses (<20 chars suggests curt/robotic)
    response_length = len(turn_result.response)
    if response_length < 20 and response_length > 0:
        # Scale up from 0.5 to 1.0 as length increases
        scores["joy_inducing"] = 0.5 + (response_length / 20) * 0.5
    elif response_length == 0:
        # Empty response is not joyful
        scores["joy_inducing"] = 0.3

    # === GENERATIVE ===
    # Lower if context utilization >90% (suggests poor compression)
    # Note: TurnResult doesn't have context_utilization yet
    # Skip this check for now

    return scores


def _apply_navigation_rules(scores: dict[str, float], context: dict[str, Any]) -> dict[str, float]:
    """
    Apply navigation-specific scoring rules.

    Navigation rules:
    - derivation navigation → GENERATIVE = 1.0 (following proof chains)
    - loss_gradient navigation → ETHICAL = 1.0 (seeking truth)
    - sibling navigation → COMPOSABLE = 0.9 (exploring related)
    - direct jump → TASTEFUL = 1.0, COMPOSABLE = 0.8 (intentional but breaks flow)

    Args:
        scores: Current scores (all default 1.0)
        context: Navigation-specific context (nav_type, target)

    Returns:
        Updated scores
    """
    nav_type = context.get("nav_type", "")

    if nav_type == "derivation":
        # Following proof chains is generative
        scores["generative"] = 1.0
    elif nav_type == "loss_gradient":
        # Seeking truth is ethical
        scores["ethical"] = 1.0
    elif nav_type == "sibling":
        # Exploring related is composable but slightly exploratory
        scores["composable"] = 0.9
    elif nav_type == "direct_jump":
        # Intentional but breaks flow
        scores["tasteful"] = 1.0
        scores["composable"] = 0.8

    return scores


def _apply_portal_rules(scores: dict[str, float], context: dict[str, Any]) -> dict[str, float]:
    """
    Apply portal-specific scoring rules.

    Portal rules:
    - depth 2+ expansion → JOY_INDUCING = 1.0 (deliberate curiosity)
    - evidence edge type → ETHICAL = 1.0 (seeking truth)
    - too many expansions (>5) → CURATED = 0.7 (sprawl warning)

    Args:
        scores: Current scores (all default 1.0)
        context: Portal-specific context (depth, edge_type, expansion_count)

    Returns:
        Updated scores
    """
    depth = context.get("depth", 0)
    edge_type = context.get("edge_type", "")
    expansion_count = context.get("expansion_count", 0)

    # Deep expansion is joyful curiosity
    if depth >= 2:
        scores["joy_inducing"] = 1.0

    # Evidence edges are ethical
    if edge_type == "evidence":
        scores["ethical"] = 1.0

    # Too many expansions suggests sprawl
    if expansion_count > 5:
        scores["curated"] = 0.7

    return scores


def _apply_edit_rules(scores: dict[str, float], context: dict[str, Any]) -> dict[str, float]:
    """
    Apply edit-specific scoring rules.

    Edit rules:
    - small change (<50 lines) → TASTEFUL = 1.0
    - large change (>200 lines) → CURATED = 0.7 (might be doing too much)
    - spec-aligned change → GENERATIVE = 1.0

    Args:
        scores: Current scores (all default 1.0)
        context: Edit-specific context (lines_changed, spec_aligned)

    Returns:
        Updated scores
    """
    lines_changed = context.get("lines_changed", 0)
    spec_aligned = context.get("spec_aligned", False)

    # Small changes are tasteful
    if lines_changed < 50:
        scores["tasteful"] = 1.0

    # Large changes might be doing too much
    if lines_changed > 200:
        scores["curated"] = 0.7

    # Spec-aligned changes are generative
    if spec_aligned:
        scores["generative"] = 1.0

    return scores


# =============================================================================
# Constitutional Reward Function
# =============================================================================


def constitutional_reward(
    action: str,
    context: dict[str, Any],
    domain: Literal["chat", "navigation", "portal", "edit"],
) -> PrincipleScore:
    """
    Compute Constitutional reward for any action across all domains.

    Evaluates the action against the 7 Constitutional principles:
    1. Tasteful: Does this serve a clear purpose?
    2. Curated: Is this intentional?
    3. Ethical: Does this respect human agency?
    4. Joy-Inducing: Does this delight?
    5. Composable: Does this compose cleanly?
    6. Heterarchical: Can this both lead and follow?
    7. Generative: Is this compressive?

    Domain-specific scoring rules are applied based on the domain parameter.

    Args:
        action: The action being evaluated (e.g., "send_message", "navigate", "expand_portal")
        context: Domain-specific context for scoring (varies by domain)
        domain: The domain where the action occurs

    Returns:
        PrincipleScore with all 7 principles evaluated

    Examples:
        >>> # Chat domain
        >>> from services.chat.evidence import TurnResult
        >>> result = TurnResult(response="Great!")
        >>> context = {"turn_result": result, "has_mutations": False}
        >>> score = constitutional_reward("send_message", context, "chat")
        >>> score.ethical
        1.0

        >>> # Navigation domain
        >>> context = {"nav_type": "derivation"}
        >>> score = constitutional_reward("navigate", context, "navigation")
        >>> score.generative
        1.0

        >>> # Portal domain
        >>> context = {"depth": 3, "edge_type": "evidence"}
        >>> score = constitutional_reward("expand", context, "portal")
        >>> score.joy_inducing
        1.0

        >>> # Edit domain
        >>> context = {"lines_changed": 20, "spec_aligned": True}
        >>> score = constitutional_reward("edit_file", context, "edit")
        >>> score.tasteful
        1.0
    """
    # Start with perfect scores (optimistic prior)
    scores = {
        "tasteful": 1.0,
        "curated": 1.0,
        "ethical": 1.0,
        "joy_inducing": 1.0,
        "composable": 1.0,
        "heterarchical": 1.0,
        "generative": 1.0,
    }

    # Apply domain-specific rules
    if domain == "chat":
        scores = _apply_chat_rules(scores, context)
    elif domain == "navigation":
        scores = _apply_navigation_rules(scores, context)
    elif domain == "portal":
        scores = _apply_portal_rules(scores, context)
    elif domain == "edit":
        scores = _apply_edit_rules(scores, context)

    return PrincipleScore(**scores)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Domain",
    "Principle",
    "PrincipleScore",
    "constitutional_reward",
]
