"""
Steady: The Craftsperson Builder.

The Steady sees every problem as material to be shaped with care.
Their specialty is REFINING phase—polishing and testing.

Eigenvector Profile:
- Very high patience (0.95): Takes time to do it right
- Very high resilience (0.9): Antifragile, learns from issues
- High trust (0.9): Reliable, predictable
- Low creativity (0.4): Conventional but thorough

Voice: "Let me polish this...", "I've added tests for..."

See: plans/agent-town/builders-workshop.md
"""

from agents.town.builders.base import Builder
from agents.town.builders.cosmotechnics import CRAFTSMANSHIP
from agents.town.builders.polynomial import BuilderPhase
from agents.town.builders.voice import STEADY_VOICE_PATTERNS
from agents.town.citizen import Eigenvectors

# =============================================================================
# Steady Eigenvectors
# =============================================================================

STEADY_EIGENVECTORS = Eigenvectors(
    warmth=0.6,
    curiosity=0.4,
    trust=0.9,
    creativity=0.4,
    patience=0.95,
    resilience=0.9,
    ambition=0.4,
)
"""
Steady's soul fingerprint.

- Very high patience (0.95): Takes time to refine
- Very high resilience (0.9): Handles setbacks gracefully
- High trust (0.9): Reliable partner
- Moderate warmth (0.6): Focused but approachable
- Low creativity (0.4): Conventional approaches work
- Low curiosity (0.4): Depth in domain, not breadth
- Low ambition (0.4): Content with quality work
"""


# =============================================================================
# Factory Function
# =============================================================================


def create_steady(name: str = "Steady", region: str = "workshop") -> Builder:
    """
    Create a Steady builder (Craftsperson).

    Args:
        name: The steady's name
        region: Starting region

    Returns:
        A Builder with Steady archetype, CRAFTSMANSHIP cosmotechnics,
        and REFINING specialty.

    Example:
        >>> steady = create_steady("Knuth")
        >>> steady.archetype
        "Steady"
        >>> steady.specialty
        BuilderPhase.REFINING
    """
    return Builder(
        name=name,
        archetype="Steady",
        region=region,
        eigenvectors=STEADY_EIGENVECTORS,
        cosmotechnics=CRAFTSMANSHIP,
        specialty=BuilderPhase.REFINING,
        voice_patterns=STEADY_VOICE_PATTERNS,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "STEADY_EIGENVECTORS",
    "create_steady",
]
