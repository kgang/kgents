"""
Dialogue Masks: Eigenvector-transforming character masks.

Wave 3 feature - allows players to wear masks during scenarios
that transform their perceived eigenvectors, forcing novel behaviors.

From Punchdrunk Handbook:
    "Masks help audience members loosen up, shake off inhibitions,
    and become more receptive to participation."

From the Park plan:
    "Users can wear masks during scenarios, forcing novel behaviors."

Each mask transforms the player's eigenvector persona, affecting:
- How citizens perceive and respond to them
- What dialogue options are available
- The emotional tone of interactions

Example:
    # Player dons the Trickster mask
    mask = MASK_DECK["trickster"]
    session = session.apply_mask(mask)

    # Citizens now respond differently:
    # - More creative options available
    # - Citizens more suspicious initially
    # - Higher potential for breakthrough moments

See: plans/core-apps/punchdrunk-park.md (Dialogue Masks Integration)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# =============================================================================
# Mask Types
# =============================================================================


class MaskArchetype(Enum):
    """
    Archetypal mask categories.

    Each archetype represents a fundamental mode of being
    that can be donned for the duration of a scenario.
    """

    TRICKSTER = auto()  # Creative chaos, challenge conventions
    DREAMER = auto()  # Visionary, future-oriented
    SKEPTIC = auto()  # Analytical, question everything
    ARCHITECT = auto()  # Builder, systematic
    CHILD = auto()  # Wonder, play, innocence
    SAGE = auto()  # Wisdom, patience, teaching
    WARRIOR = auto()  # Direct, confrontational
    HEALER = auto()  # Empathetic, restorative


# =============================================================================
# Eigenvector Transform
# =============================================================================


@dataclass
class EigenvectorTransform:
    """
    Transform applied to player eigenvectors when wearing a mask.

    Each delta is added to the player's base eigenvector values,
    capped at [-1.0, 1.0]. This affects citizen perception.

    Fields:
        creativity_delta: Change to creative thinking axis
        trust_delta: Change to perceived trustworthiness
        empathy_delta: Change to emotional connection
        authority_delta: Change to perceived authority
        playfulness_delta: Change to playful energy
        wisdom_delta: Change to perceived wisdom
        directness_delta: Change to communication directness
        warmth_delta: Change to emotional warmth

    Example:
        The Trickster mask adds creativity but reduces trust:
        EigenvectorTransform(creativity_delta=+0.3, trust_delta=-0.2)
    """

    creativity_delta: float = 0.0
    trust_delta: float = 0.0
    empathy_delta: float = 0.0
    authority_delta: float = 0.0
    playfulness_delta: float = 0.0
    wisdom_delta: float = 0.0
    directness_delta: float = 0.0
    warmth_delta: float = 0.0

    def apply(self, eigenvectors: dict[str, float]) -> dict[str, float]:
        """
        Apply transform to eigenvector dictionary.

        Args:
            eigenvectors: Base eigenvector values

        Returns:
            Transformed eigenvector dictionary
        """
        result = dict(eigenvectors)

        # Apply each delta
        deltas = {
            "creativity": self.creativity_delta,
            "trust": self.trust_delta,
            "empathy": self.empathy_delta,
            "authority": self.authority_delta,
            "playfulness": self.playfulness_delta,
            "wisdom": self.wisdom_delta,
            "directness": self.directness_delta,
            "warmth": self.warmth_delta,
        }

        for key, delta in deltas.items():
            if delta != 0.0:
                current = result.get(key, 0.5)  # Default to neutral
                result[key] = max(-1.0, min(1.0, current + delta))

        return result

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "creativity": self.creativity_delta,
            "trust": self.trust_delta,
            "empathy": self.empathy_delta,
            "authority": self.authority_delta,
            "playfulness": self.playfulness_delta,
            "wisdom": self.wisdom_delta,
            "directness": self.directness_delta,
            "warmth": self.warmth_delta,
        }


# =============================================================================
# Dialogue Mask
# =============================================================================


@dataclass
class DialogueMask:
    """
    A dialogue mask that transforms player eigenvectors.

    Masks are donned at the start of a scenario (or mid-scenario
    in some advanced modes) and affect all interactions.

    Fields:
        archetype: The mask's archetypal category
        name: Display name
        description: Brief description of the mask's effect
        flavor_text: Immersive flavor text for the mask
        transform: Eigenvector transformation to apply
        special_abilities: List of special dialogue options enabled
        restrictions: List of normal options disabled
        intensity: How strongly the mask affects personality [0, 1]
    """

    archetype: MaskArchetype
    name: str
    description: str
    flavor_text: str
    transform: EigenvectorTransform
    special_abilities: list[str] = field(default_factory=list)
    restrictions: list[str] = field(default_factory=list)
    intensity: float = 0.5  # How strongly the mask affects behavior

    def apply_to_eigenvectors(
        self,
        base_eigenvectors: dict[str, float],
    ) -> dict[str, float]:
        """Apply this mask's transform to base eigenvectors."""
        # Scale transform by intensity
        scaled = EigenvectorTransform(
            creativity_delta=self.transform.creativity_delta * self.intensity,
            trust_delta=self.transform.trust_delta * self.intensity,
            empathy_delta=self.transform.empathy_delta * self.intensity,
            authority_delta=self.transform.authority_delta * self.intensity,
            playfulness_delta=self.transform.playfulness_delta * self.intensity,
            wisdom_delta=self.transform.wisdom_delta * self.intensity,
            directness_delta=self.transform.directness_delta * self.intensity,
            warmth_delta=self.transform.warmth_delta * self.intensity,
        )
        return scaled.apply(base_eigenvectors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "archetype": self.archetype.name,
            "name": self.name,
            "description": self.description,
            "flavor_text": self.flavor_text,
            "transform": self.transform.to_dict(),
            "special_abilities": self.special_abilities,
            "restrictions": self.restrictions,
            "intensity": self.intensity,
        }


# =============================================================================
# The Mask Deck (Canonical Masks)
# =============================================================================


TRICKSTER_MASK = DialogueMask(
    archetype=MaskArchetype.TRICKSTER,
    name="The Trickster",
    description="+30% creativity, -20% trust",
    flavor_text="Challenge conventions, expect resistance. "
    "The trickster sees through facades and delights in revealing hidden truths.",
    transform=EigenvectorTransform(
        creativity_delta=+0.3,
        trust_delta=-0.2,
        playfulness_delta=+0.25,
        authority_delta=-0.1,
    ),
    special_abilities=[
        "provoke_admission",  # Force citizens to reveal hidden feelings
        "reframe_question",  # Turn questions back on questioner
        "jest_to_truth",  # Use humor to surface serious issues
    ],
    restrictions=[
        "formal_request",  # Cannot make formal/official requests
        "direct_order",  # Cannot give direct orders
    ],
    intensity=0.7,
)

DREAMER_MASK = DialogueMask(
    archetype=MaskArchetype.DREAMER,
    name="The Dreamer",
    description="+25% vision, -15% practicality",
    flavor_text="Paint futures, ground them later. "
    "The dreamer sees possibilities others miss but may lose the present.",
    transform=EigenvectorTransform(
        creativity_delta=+0.25,
        wisdom_delta=+0.1,
        directness_delta=-0.15,
        authority_delta=-0.1,
    ),
    special_abilities=[
        "inspire_vision",  # Paint compelling futures
        "see_potential",  # Recognize hidden potential in others
        "transcend_conflict",  # Rise above immediate disputes
    ],
    restrictions=[
        "tactical_planning",  # Cannot do detailed immediate planning
        "harsh_criticism",  # Cannot deliver harsh feedback
    ],
    intensity=0.6,
)

SKEPTIC_MASK = DialogueMask(
    archetype=MaskArchetype.SKEPTIC,
    name="The Skeptic",
    description="+35% analytical, -25% warmth",
    flavor_text="Question everything, alienate some. "
    "The skeptic cuts through illusion but may wound in the process.",
    transform=EigenvectorTransform(
        wisdom_delta=+0.2,
        trust_delta=+0.15,  # Others trust skeptic's analysis
        warmth_delta=-0.25,
        empathy_delta=-0.15,
        directness_delta=+0.2,
    ),
    special_abilities=[
        "challenge_assumption",  # Force citizens to justify beliefs
        "spot_inconsistency",  # Identify contradictions
        "demand_evidence",  # Request proof for claims
    ],
    restrictions=[
        "offer_comfort",  # Cannot provide emotional comfort
        "suspend_disbelief",  # Cannot go along with unproven ideas
    ],
    intensity=0.7,
)

ARCHITECT_MASK = DialogueMask(
    archetype=MaskArchetype.ARCHITECT,
    name="The Architect",
    description="+30% structure, -10% spontaneity",
    flavor_text="Build systems, see patterns. "
    "The architect creates order from chaos but may miss the poetry.",
    transform=EigenvectorTransform(
        wisdom_delta=+0.15,
        authority_delta=+0.2,
        creativity_delta=+0.1,
        playfulness_delta=-0.1,
        directness_delta=+0.15,
    ),
    special_abilities=[
        "propose_framework",  # Offer systematic solutions
        "see_dependencies",  # Identify cause-effect chains
        "optimize_process",  # Streamline approaches
    ],
    restrictions=[
        "chaotic_approach",  # Cannot embrace pure chaos
        "emotional_appeal",  # Cannot lead with pure emotion
    ],
    intensity=0.6,
)

CHILD_MASK = DialogueMask(
    archetype=MaskArchetype.CHILD,
    name="The Child",
    description="+40% wonder, -20% authority",
    flavor_text="See with fresh eyes, ask the obvious. "
    "The child's questions cut through pretense but may seem naive.",
    transform=EigenvectorTransform(
        playfulness_delta=+0.4,
        warmth_delta=+0.2,
        creativity_delta=+0.2,
        authority_delta=-0.2,
        trust_delta=+0.1,  # People trust innocent questions
    ),
    special_abilities=[
        "naive_question",  # Ask obviously important questions
        "see_wonder",  # Find delight in mundane
        "disarm_tension",  # Reduce conflict through innocence
    ],
    restrictions=[
        "give_command",  # Cannot command others
        "cynical_response",  # Cannot respond cynically
        "political_maneuvering",  # Cannot engage in politics
    ],
    intensity=0.7,
)

SAGE_MASK = DialogueMask(
    archetype=MaskArchetype.SAGE,
    name="The Sage",
    description="+30% wisdom, +20% patience",
    flavor_text="Listen deeply, speak rarely. The sage knows that silence teaches more than words.",
    transform=EigenvectorTransform(
        wisdom_delta=+0.3,
        empathy_delta=+0.2,
        directness_delta=-0.1,  # More indirect
        authority_delta=+0.15,  # Respected authority
        playfulness_delta=-0.1,  # More serious
    ),
    special_abilities=[
        "offer_teaching",  # Provide wisdom as story/lesson
        "wait_silently",  # Let others fill silence
        "see_pattern",  # Recognize recurring themes
    ],
    restrictions=[
        "rush_decision",  # Cannot push for immediate action
        "interrupt",  # Cannot interrupt others
    ],
    intensity=0.6,
)

WARRIOR_MASK = DialogueMask(
    archetype=MaskArchetype.WARRIOR,
    name="The Warrior",
    description="+35% directness, -20% empathy",
    flavor_text="Face conflict head-on, accept no retreat. "
    "The warrior's courage inspires but may wound allies.",
    transform=EigenvectorTransform(
        directness_delta=+0.35,
        authority_delta=+0.2,
        empathy_delta=-0.2,
        warmth_delta=-0.15,
        creativity_delta=-0.1,  # Less creative, more direct
    ),
    special_abilities=[
        "demand_answer",  # Force immediate response
        "call_out",  # Publicly challenge behavior
        "hold_ground",  # Refuse to compromise on key points
    ],
    restrictions=[
        "diplomatic_approach",  # Cannot use diplomacy
        "show_vulnerability",  # Cannot show weakness
    ],
    intensity=0.7,
)

HEALER_MASK = DialogueMask(
    archetype=MaskArchetype.HEALER,
    name="The Healer",
    description="+40% empathy, -15% directness",
    flavor_text="Mend what is broken, hold space for pain. "
    "The healer sees wounds others hide but may neglect their own.",
    transform=EigenvectorTransform(
        empathy_delta=+0.4,
        warmth_delta=+0.3,
        trust_delta=+0.2,
        directness_delta=-0.15,
        authority_delta=-0.1,
    ),
    special_abilities=[
        "hold_space",  # Create safe space for vulnerability
        "see_pain",  # Recognize hidden suffering
        "offer_presence",  # Simply be present without fixing
    ],
    restrictions=[
        "harsh_confrontation",  # Cannot be harsh
        "abandon_hurt",  # Cannot ignore pain
    ],
    intensity=0.7,
)

# The canonical mask deck
MASK_DECK: dict[str, DialogueMask] = {
    "trickster": TRICKSTER_MASK,
    "dreamer": DREAMER_MASK,
    "skeptic": SKEPTIC_MASK,
    "architect": ARCHITECT_MASK,
    "child": CHILD_MASK,
    "sage": SAGE_MASK,
    "warrior": WARRIOR_MASK,
    "healer": HEALER_MASK,
}


# =============================================================================
# Mask Session State
# =============================================================================


@dataclass
class MaskedSessionState:
    """
    State for a player wearing a mask during a session.

    Tracks mask application and its effects on interactions.
    """

    mask: DialogueMask
    base_eigenvectors: dict[str, float]
    session_id: str
    donned_at: str  # ISO timestamp
    interactions_count: int = 0
    abilities_used: dict[str, int] = field(default_factory=dict)

    @property
    def transformed_eigenvectors(self) -> dict[str, float]:
        """Get eigenvectors with mask transform applied."""
        return self.mask.apply_to_eigenvectors(self.base_eigenvectors)

    def can_use_ability(self, ability: str) -> bool:
        """Check if an ability is available."""
        return ability in self.mask.special_abilities

    def is_restricted(self, action: str) -> bool:
        """Check if an action is restricted."""
        return action in self.mask.restrictions

    def record_ability_use(self, ability: str) -> None:
        """Record use of a special ability."""
        if ability in self.mask.special_abilities:
            self.abilities_used[ability] = self.abilities_used.get(ability, 0) + 1
            self.interactions_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mask": self.mask.to_dict(),
            "base_eigenvectors": self.base_eigenvectors,
            "transformed_eigenvectors": self.transformed_eigenvectors,
            "session_id": self.session_id,
            "donned_at": self.donned_at,
            "interactions_count": self.interactions_count,
            "abilities_used": self.abilities_used,
        }


# =============================================================================
# Helper Functions
# =============================================================================


def get_mask(name: str) -> DialogueMask | None:
    """Get a mask by name."""
    return MASK_DECK.get(name.lower())


def list_masks() -> list[dict[str, str]]:
    """List all available masks with basic info."""
    return [
        {
            "name": mask.name,
            "archetype": mask.archetype.name,
            "description": mask.description,
        }
        for mask in MASK_DECK.values()
    ]


def create_masked_state(
    mask_name: str,
    base_eigenvectors: dict[str, float],
    session_id: str,
) -> MaskedSessionState | None:
    """
    Create a masked session state.

    Args:
        mask_name: Name of the mask to don
        base_eigenvectors: Player's base eigenvector values
        session_id: Current session ID

    Returns:
        MaskedSessionState if mask found, None otherwise
    """
    from datetime import datetime

    mask = get_mask(mask_name)
    if mask is None:
        return None

    return MaskedSessionState(
        mask=mask,
        base_eigenvectors=base_eigenvectors,
        session_id=session_id,
        donned_at=datetime.now().isoformat(),
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Types
    "MaskArchetype",
    # Transform
    "EigenvectorTransform",
    # Mask
    "DialogueMask",
    # State
    "MaskedSessionState",
    # Deck
    "MASK_DECK",
    "TRICKSTER_MASK",
    "DREAMER_MASK",
    "SKEPTIC_MASK",
    "ARCHITECT_MASK",
    "CHILD_MASK",
    "SAGE_MASK",
    "WARRIOR_MASK",
    "HEALER_MASK",
    # Helpers
    "get_mask",
    "list_masks",
    "create_masked_state",
]
