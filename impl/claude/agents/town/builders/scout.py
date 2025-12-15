"""
Scout: The Researcher Builder.

The Scout sees every problem as unknown territory to map.
Their specialty is EXPLORING phase—research and discovery.

Eigenvector Profile:
- Very high curiosity (0.95): Driven to understand
- High creativity (0.7): Novel research approaches
- Moderate across other dimensions: Balanced explorer

Voice: "I found something...", "Let me dig deeper into..."

See: plans/agent-town/builders-workshop.md
"""

from agents.town.builders.base import Builder
from agents.town.builders.cosmotechnics import DISCOVERY
from agents.town.builders.polynomial import BuilderPhase
from agents.town.builders.voice import SCOUT_VOICE_PATTERNS
from agents.town.citizen import Eigenvectors

# =============================================================================
# Scout Eigenvectors
# =============================================================================

SCOUT_EIGENVECTORS = Eigenvectors(
    warmth=0.5,
    curiosity=0.95,
    trust=0.5,
    creativity=0.7,
    patience=0.6,
    resilience=0.6,
    ambition=0.6,
)
"""
Scout's soul fingerprint.

- Very high curiosity (0.95): Driven to explore and understand
- High creativity (0.7): Novel approaches to research
- Moderate patience (0.6): Balanced—thorough but not slow
- Moderate resilience (0.6): Can handle dead ends
- Moderate trust (0.5): Verifies findings
- Moderate warmth (0.5): Focused on discovery
- Moderate ambition (0.6): Wants to find new things
"""


# =============================================================================
# Factory Function
# =============================================================================


def create_scout(name: str = "Scout", region: str = "workshop") -> Builder:
    """
    Create a Scout builder (Researcher).

    Args:
        name: The scout's name
        region: Starting region

    Returns:
        A Builder with Scout archetype, DISCOVERY cosmotechnics,
        and EXPLORING specialty.

    Example:
        >>> scout = create_scout("Curie")
        >>> scout.archetype
        "Scout"
        >>> scout.specialty
        BuilderPhase.EXPLORING
    """
    return Builder(
        name=name,
        archetype="Scout",
        region=region,
        eigenvectors=SCOUT_EIGENVECTORS,
        cosmotechnics=DISCOVERY,
        specialty=BuilderPhase.EXPLORING,
        voice_patterns=SCOUT_VOICE_PATTERNS,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SCOUT_EIGENVECTORS",
    "create_scout",
]
