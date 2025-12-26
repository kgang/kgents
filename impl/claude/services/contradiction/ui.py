"""
Contradiction UI Generation: Backend-Driven Frontend State.

Generates UI data structures for contradiction cards and resolution dialogs.
Following the Metaphysical Fullstack pattern: backend owns the presentation logic,
frontend is a thin projection layer.

Philosophy:
    "The backend doesn't just serve data — it serves PRESENTATION STATE."
    - docs/skills/metaphysical-fullstack.md

    This module generates everything the frontend needs to render:
    - Contradiction cards with proper styling
    - Resolution dialogs with contextual guidance
    - Status indicators and progress states

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .classification import ClassificationResult, ContradictionType
    from .detection import ContradictionPair
    from .resolution import ResolutionPrompt, ResolutionStrategy


@dataclass(frozen=True)
class ContradictionCardUI:
    """
    UI data for rendering a contradiction card.

    This is the complete state the frontend needs — no additional
    processing or logic required. The frontend is purely presentational.
    """

    # Identity
    id: str
    title: str

    # Content
    statement_a: str
    statement_a_label: str  # e.g., "Your Axiom (L1)"
    statement_b: str
    statement_b_label: str  # e.g., "Your Value (L2)"

    # Strength visualization
    strength: float
    strength_label: str  # e.g., "Productive Tension (0.32)"
    strength_percentage: int  # For progress bars (0-100)

    # Classification
    classification_type: str  # "APPARENT", "PRODUCTIVE", etc.
    classification_color: str  # "gray", "green", "yellow", "red"
    classification_description: str

    # Guidance
    guidance_title: str  # "This is INFORMATION, not JUDGMENT"
    guidance_text: str  # Contextual explanation
    suggested_action: str  # e.g., "Try synthesizing..."

    # Actions (button configurations)
    actions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, object]:
        """Serialize for API/frontend."""
        return {
            "id": self.id,
            "title": self.title,
            "statement_a": self.statement_a,
            "statement_a_label": self.statement_a_label,
            "statement_b": self.statement_b,
            "statement_b_label": self.statement_b_label,
            "strength": round(self.strength, 3),
            "strength_label": self.strength_label,
            "strength_percentage": self.strength_percentage,
            "classification": {
                "type": self.classification_type,
                "color": self.classification_color,
                "description": self.classification_description,
            },
            "guidance": {
                "title": self.guidance_title,
                "text": self.guidance_text,
                "suggested_action": self.suggested_action,
            },
            "actions": self.actions,
        }


@dataclass(frozen=True)
class ResolutionDialogUI:
    """
    UI data for rendering a resolution dialog.

    Contains everything needed for the modal/dialog interface
    where users choose how to resolve the contradiction.
    """

    # Identity
    contradiction_id: str

    # Header
    title: str
    subtitle: str

    # Content (same as card)
    statement_a: str
    statement_a_label: str
    statement_b: str
    statement_b_label: str

    # Strength (same as card)
    strength: float
    strength_label: str
    classification_color: str

    # Resolution options (expanded with details)
    options: list[dict[str, Any]]

    # Suggested option (highlighted)
    suggested_option: str  # "SYNTHESIZE", "SCOPE", etc.
    suggestion_reasoning: str

    def to_dict(self) -> dict[str, object]:
        """Serialize for API/frontend."""
        return {
            "contradiction_id": self.contradiction_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "statement_a": self.statement_a,
            "statement_a_label": self.statement_a_label,
            "statement_b": self.statement_b,
            "statement_b_label": self.statement_b_label,
            "strength": round(self.strength, 3),
            "strength_label": self.strength_label,
            "classification_color": self.classification_color,
            "options": self.options,
            "suggested_option": self.suggested_option,
            "suggestion_reasoning": self.suggestion_reasoning,
        }


class ContradictionUIGenerator:
    """
    Generates UI data structures for contradiction presentation.

    This is where the "design system" lives for contradictions:
    - Color mappings
    - Label formatting
    - Action button configurations
    - Guidance text templates
    """

    # Design constants
    GUIDANCE_TITLE = "This is INFORMATION, not JUDGMENT"
    GUIDANCE_BASE = (
        "Your beliefs are allowed to be in flux. "
        "Contradictions are invitations to grow, not errors to fix."
    )

    def generate_card(
        self,
        pair: ContradictionPair,
        classification: ClassificationResult,
        prompt: ResolutionPrompt,
    ) -> ContradictionCardUI:
        """
        Generate UI data for a contradiction card.

        Args:
            pair: The contradiction pair
            classification: Classification result
            prompt: Resolution prompt

        Returns:
            ContradictionCardUI with complete presentation state
        """
        # Format labels
        label_a = self._format_label(pair.kblock_a)
        label_b = self._format_label(pair.kblock_b)

        # Strength visualization
        strength_label = f"{classification.type.value.title()} ({pair.strength:.2f})"
        strength_percentage = min(100, int(pair.strength * 100))

        # Actions (compact for card)
        actions = [
            {
                "value": "resolve",
                "label": "Resolve",
                "icon": "arrow-right",
                "variant": "primary",
            },
            {
                "value": "ignore",
                "label": "Later",
                "icon": "clock",
                "variant": "ghost",
            },
        ]

        return ContradictionCardUI(
            id=pair.id,
            title="Contradiction Detected",
            statement_a=self._truncate(pair.kblock_a.content),
            statement_a_label=label_a,
            statement_b=self._truncate(pair.kblock_b.content),
            statement_b_label=label_b,
            strength=pair.strength,
            strength_label=strength_label,
            strength_percentage=strength_percentage,
            classification_type=classification.type.value,
            classification_color=classification.type.color,
            classification_description=classification.type.description,
            guidance_title=self.GUIDANCE_TITLE,
            guidance_text=self.GUIDANCE_BASE,
            suggested_action=prompt.reasoning,
            actions=actions,
        )

    def generate_dialog(
        self,
        prompt: ResolutionPrompt,
    ) -> ResolutionDialogUI:
        """
        Generate UI data for a resolution dialog.

        Args:
            prompt: Resolution prompt with full context

        Returns:
            ResolutionDialogUI with complete presentation state
        """
        pair = prompt.pair
        classification = prompt.classification

        # Format labels
        label_a = self._format_label(pair.kblock_a)
        label_b = self._format_label(pair.kblock_b)

        # Strength visualization
        strength_label = f"{classification.type.value.title()} ({pair.strength:.2f})"

        # Resolution options (all available strategies)
        from .resolution import ResolutionStrategy

        options = []
        for strategy in ResolutionStrategy:
            is_suggested = strategy == prompt.suggested_strategy
            options.append(
                {
                    "value": strategy.value,
                    "label": strategy.action_verb,
                    "description": strategy.description,
                    "icon": strategy.icon,
                    "suggested": is_suggested,
                }
            )

        return ResolutionDialogUI(
            contradiction_id=pair.id,
            title="How would you like to resolve this?",
            subtitle=classification.type.description,
            statement_a=pair.kblock_a.content,
            statement_a_label=label_a,
            statement_b=pair.kblock_b.content,
            statement_b_label=label_b,
            strength=pair.strength,
            strength_label=strength_label,
            classification_color=classification.type.color,
            options=options,
            suggested_option=prompt.suggested_strategy.value,
            suggestion_reasoning=prompt.reasoning,
        )

    def _format_label(self, kblock: Any) -> str:
        """Format a K-Block label with layer and kind."""
        layer = getattr(kblock, "zero_seed_layer", None)
        kind = getattr(kblock, "zero_seed_kind", None)

        if layer and kind:
            return f"{kind.title()} (L{layer})"
        elif layer:
            return f"Layer {layer}"
        else:
            # Fallback for non-Zero Seed K-Blocks
            return "Statement"

    def _truncate(self, content: str, max_chars: int = 200) -> str:
        """Truncate content for card display."""
        if len(content) <= max_chars:
            return content
        return content[:max_chars].rsplit(" ", 1)[0] + "..."


# Singleton generator for convenience
default_generator = ContradictionUIGenerator()


def generate_contradiction_card(
    pair: ContradictionPair,
    classification: ClassificationResult,
    prompt: ResolutionPrompt,
) -> ContradictionCardUI:
    """
    Convenience function to generate a contradiction card.

    Args:
        pair: The contradiction pair
        classification: Classification result
        prompt: Resolution prompt

    Returns:
        ContradictionCardUI
    """
    return default_generator.generate_card(pair, classification, prompt)


def generate_resolution_dialog(
    prompt: ResolutionPrompt,
) -> ResolutionDialogUI:
    """
    Convenience function to generate a resolution dialog.

    Args:
        prompt: Resolution prompt

    Returns:
        ResolutionDialogUI
    """
    return default_generator.generate_dialog(prompt)


__all__ = [
    "ContradictionCardUI",
    "ResolutionDialogUI",
    "ContradictionUIGenerator",
    "default_generator",
    "generate_contradiction_card",
    "generate_resolution_dialog",
]
