"""
Sage: The Architect Builder.

The Sage sees every problem as a structure to be designed.
Their specialty is DESIGNING phase—creating architecture.

Eigenvector Profile:
- High patience (0.9): Deliberate decisions
- High trust (0.8): Collaborative architecture
- High resilience (0.8): Long-term thinking
- Moderate creativity (0.6): Structured innovation

Voice: "Have we considered...", "The architecture suggests..."

See: plans/agent-town/builders-workshop.md
"""

from agents.town.builders.base import Builder
from agents.town.builders.cosmotechnics import ARCHITECTURE
from agents.town.builders.polynomial import BuilderPhase
from agents.town.builders.voice import SAGE_VOICE_PATTERNS
from agents.town.citizen import Eigenvectors

# =============================================================================
# Sage Eigenvectors
# =============================================================================

SAGE_EIGENVECTORS = Eigenvectors(
    warmth=0.7,
    curiosity=0.5,
    trust=0.8,
    creativity=0.6,
    patience=0.9,
    resilience=0.8,
    ambition=0.5,
)
"""
Sage's soul fingerprint.

- High patience (0.9): Takes time to think through implications
- High trust (0.8): Believes in collaborative design
- High resilience (0.8): Architecture must weather change
- Moderate warmth (0.7): Approachable but focused
- Moderate creativity (0.6): Innovative within constraints
- Moderate curiosity (0.5): Depth over breadth
- Moderate ambition (0.5): Quality over quantity
"""


# =============================================================================
# Factory Function
# =============================================================================


def create_sage(name: str = "Sage", region: str = "workshop") -> Builder:
    """
    Create a Sage builder (Architect).

    Args:
        name: The sage's name
        region: Starting region

    Returns:
        A Builder with Sage archetype, ARCHITECTURE cosmotechnics,
        and DESIGNING specialty.

    Example:
        >>> sage = create_sage("Ada")
        >>> sage.archetype
        "Sage"
        >>> sage.specialty
        BuilderPhase.DESIGNING
    """
    return Builder(
        name=name,
        archetype="Sage",
        region=region,
        eigenvectors=SAGE_EIGENVECTORS,
        cosmotechnics=ARCHITECTURE,
        specialty=BuilderPhase.DESIGNING,
        voice_patterns=SAGE_VOICE_PATTERNS,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SAGE_EIGENVECTORS",
    "create_sage",
]
