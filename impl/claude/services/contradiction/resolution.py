"""
Contradiction Resolution: Five Paths Forward.

When a contradiction is detected, the user chooses how to resolve it:

1. SYNTHESIZE: Create a new K-Block that resolves both
2. SCOPE: Clarify these apply in different contexts
3. CHOOSE: Decide which you actually believe
4. TOLERATE: Keep both as productive tension
5. IGNORE: Think about it later

Philosophy:
    "Mirrors don't tell you to change. Mirrors show you what is."
    - Zero Seed Grand Strategy, Part II, LAW 4

    The system NEVER forces resolution.
    The system ALWAYS respects user autonomy.
    The system OFFERS paths, user CHOOSES path.

See: plans/zero-seed-genesis-grand-strategy.md (Part VIII)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.k_block.core.kblock import KBlock
    from services.witness.mark import MarkId

    from .classification import ClassificationResult
    from .detection import ContradictionPair


class ResolutionStrategy(Enum):
    """
    The five resolution strategies.

    Each strategy represents a different relationship to contradiction.
    No strategy is "better" — context determines appropriateness.
    """

    SYNTHESIZE = "SYNTHESIZE"  # Create higher truth
    SCOPE = "SCOPE"  # Clarify contexts
    CHOOSE = "CHOOSE"  # Pick one belief
    TOLERATE = "TOLERATE"  # Accept tension
    IGNORE = "IGNORE"  # Defer decision

    @property
    def description(self) -> str:
        """Human-readable description."""
        match self:
            case ResolutionStrategy.SYNTHESIZE:
                return "Find a higher truth that resolves both"
            case ResolutionStrategy.SCOPE:
                return "Clarify that these apply in different contexts"
            case ResolutionStrategy.CHOOSE:
                return "Decide which you actually believe"
            case ResolutionStrategy.TOLERATE:
                return "Keep both — productive tension is valuable"
            case ResolutionStrategy.IGNORE:
                return "I'll think about this later"

    @property
    def action_verb(self) -> str:
        """Action verb for UI buttons."""
        match self:
            case ResolutionStrategy.SYNTHESIZE:
                return "Synthesize"
            case ResolutionStrategy.SCOPE:
                return "Scope"
            case ResolutionStrategy.CHOOSE:
                return "Choose"
            case ResolutionStrategy.TOLERATE:
                return "Tolerate"
            case ResolutionStrategy.IGNORE:
                return "Ignore"

    @property
    def icon(self) -> str:
        """Icon name for UI."""
        match self:
            case ResolutionStrategy.SYNTHESIZE:
                return "merge"
            case ResolutionStrategy.SCOPE:
                return "scope"
            case ResolutionStrategy.CHOOSE:
                return "check-circle"
            case ResolutionStrategy.TOLERATE:
                return "balance"
            case ResolutionStrategy.IGNORE:
                return "clock"


@dataclass(frozen=True)
class ResolutionOutcome:
    """
    The result of applying a resolution strategy.

    Different strategies produce different outcomes:
    - SYNTHESIZE: new_kblock created
    - SCOPE: scope_note added to both K-Blocks
    - CHOOSE: chosen_kblock indicated, other marked as superseded
    - TOLERATE: contradiction marked as accepted
    - IGNORE: contradiction deferred for later
    """

    strategy: ResolutionStrategy
    resolved_at: datetime
    witness_mark: MarkId  # Every resolution is witnessed
    new_kblock: KBlock | None = None  # For SYNTHESIZE
    scope_note: str | None = None  # For SCOPE
    chosen_kblock: KBlock | None = None  # For CHOOSE
    deferred_until: datetime | None = None  # For IGNORE
    metadata: dict[str, Any] | None = None  # Additional context

    def to_dict(self) -> dict[str, object]:
        """Serialize for API/storage."""
        result: dict[str, object] = {
            "strategy": self.strategy.value,
            "resolved_at": self.resolved_at.isoformat(),
            "witness_mark": self.witness_mark,
            "metadata": self.metadata or {},
        }

        if self.new_kblock:
            result["new_kblock_id"] = self.new_kblock.id
        if self.scope_note:
            result["scope_note"] = self.scope_note
        if self.chosen_kblock:
            result["chosen_kblock_id"] = self.chosen_kblock.id
        if self.deferred_until:
            result["deferred_until"] = self.deferred_until.isoformat()

        return result


@dataclass(frozen=True)
class ResolutionPrompt:
    """
    A prompt for the user to resolve a contradiction.

    Includes:
    - The contradiction pair
    - Classification (strength/type)
    - Available strategies
    - Contextual guidance
    """

    pair: ContradictionPair
    classification: ClassificationResult
    suggested_strategy: ResolutionStrategy
    reasoning: str

    def to_dict(self) -> dict[str, object]:
        """Serialize for API/frontend."""
        return {
            "contradiction_id": self.pair.id,
            "kblock_a": {
                "id": self.pair.kblock_a.id,
                "content": self.pair.kblock_a.content,
                "layer": getattr(self.pair.kblock_a, "zero_seed_layer", None),
            },
            "kblock_b": {
                "id": self.pair.kblock_b.id,
                "content": self.pair.kblock_b.content,
                "layer": getattr(self.pair.kblock_b, "zero_seed_layer", None),
            },
            "strength": round(self.pair.strength, 3),
            "classification": self.classification.to_dict(),
            "suggested_strategy": self.suggested_strategy.value,
            "reasoning": self.reasoning,
            "available_strategies": [
                {
                    "value": s.value,
                    "description": s.description,
                    "action_verb": s.action_verb,
                    "icon": s.icon,
                }
                for s in ResolutionStrategy
            ],
        }


class ResolutionEngine:
    """
    Guides users through contradiction resolution.

    The engine:
    1. Receives a contradiction pair + classification
    2. Suggests appropriate resolution strategy
    3. Generates resolution prompt for user
    4. Executes chosen strategy
    5. Witnesses the resolution
    """

    def __init__(self) -> None:
        """Initialize resolution engine."""
        pass

    def suggest_strategy(
        self,
        pair: ContradictionPair,
        classification: ClassificationResult,
    ) -> ResolutionStrategy:
        """
        Suggest a resolution strategy based on classification.

        Heuristics:
        - APPARENT contradictions → SCOPE (likely different contexts)
        - PRODUCTIVE contradictions → SYNTHESIZE (opportunity for growth)
        - TENSION contradictions → TOLERATE or CHOOSE (deliberate engagement)
        - FUNDAMENTAL contradictions → CHOOSE (deep conflict requires decision)

        Args:
            pair: The contradiction pair
            classification: The classification result

        Returns:
            Suggested ResolutionStrategy
        """
        from .classification import ContradictionType

        match classification.type:
            case ContradictionType.APPARENT:
                return ResolutionStrategy.SCOPE
            case ContradictionType.PRODUCTIVE:
                return ResolutionStrategy.SYNTHESIZE
            case ContradictionType.TENSION:
                # For tension, suggest TOLERATE if layers are close (same domain)
                # Otherwise suggest CHOOSE
                layer_a = getattr(pair.kblock_a, "zero_seed_layer", 5)
                layer_b = getattr(pair.kblock_b, "zero_seed_layer", 5)
                if abs(layer_a - layer_b) <= 1:
                    return ResolutionStrategy.TOLERATE
                else:
                    return ResolutionStrategy.CHOOSE
            case ContradictionType.FUNDAMENTAL:
                return ResolutionStrategy.CHOOSE

    def create_prompt(
        self,
        pair: ContradictionPair,
        classification: ClassificationResult,
    ) -> ResolutionPrompt:
        """
        Create a resolution prompt for the user.

        Args:
            pair: The contradiction pair
            classification: The classification result

        Returns:
            ResolutionPrompt with suggestion and reasoning
        """
        strategy = self.suggest_strategy(pair, classification)

        # Generate contextual reasoning
        reasoning = self._generate_reasoning(pair, classification, strategy)

        return ResolutionPrompt(
            pair=pair,
            classification=classification,
            suggested_strategy=strategy,
            reasoning=reasoning,
        )

    def _generate_reasoning(
        self,
        pair: ContradictionPair,
        classification: ClassificationResult,
        strategy: ResolutionStrategy,
    ) -> str:
        """Generate human-readable reasoning for the suggestion."""
        from .classification import ContradictionType

        base = classification.reasoning

        match classification.type:
            case ContradictionType.APPARENT:
                return (
                    f"{base}\n\nSuggestion: Add scope notes to clarify when each statement applies."
                )
            case ContradictionType.PRODUCTIVE:
                return f"{base}\n\nSuggestion: Try synthesizing these into a higher truth that honors both."
            case ContradictionType.TENSION:
                return f"{base}\n\nYou can either tolerate this tension as productive, or choose which belief to prioritize."
            case ContradictionType.FUNDAMENTAL:
                return f"{base}\n\nThis requires careful examination. Which belief is more fundamental to your worldview?"


# Singleton engine for convenience
default_engine = ResolutionEngine()


def create_resolution_prompt(
    pair: ContradictionPair,
    classification: ClassificationResult,
) -> ResolutionPrompt:
    """
    Convenience function to create a resolution prompt.

    Args:
        pair: The contradiction pair
        classification: The classification result

    Returns:
        ResolutionPrompt
    """
    return default_engine.create_prompt(pair, classification)


__all__ = [
    "ResolutionStrategy",
    "ResolutionOutcome",
    "ResolutionPrompt",
    "ResolutionEngine",
    "default_engine",
    "create_resolution_prompt",
]
