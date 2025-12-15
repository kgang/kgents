"""
Spark: The Experimenter Builder.

The Spark sees every problem as a space to explore through trial.
Their specialty is PROTOTYPING phase—rapid experimentation.

Eigenvector Profile:
- Very high creativity (0.95): Inventive, novel approaches
- Very high curiosity (0.9): Always exploring
- Low patience (0.3): Moves fast, iterates quickly
- High warmth (0.8): Enthusiastic collaboration

Voice: "What if we tried...", "Here's a wild idea..."

See: plans/agent-town/builders-workshop.md
"""

from agents.town.builders.base import Builder
from agents.town.builders.cosmotechnics import EXPERIMENTATION
from agents.town.builders.polynomial import BuilderPhase
from agents.town.builders.voice import SPARK_VOICE_PATTERNS
from agents.town.citizen import Eigenvectors

# =============================================================================
# Spark Eigenvectors
# =============================================================================

SPARK_EIGENVECTORS = Eigenvectors(
    warmth=0.8,
    curiosity=0.9,
    trust=0.6,
    creativity=0.95,
    patience=0.3,
    resilience=0.5,
    ambition=0.7,
)
"""
Spark's soul fingerprint.

- Very high creativity (0.95): Inventive, thinks outside the box
- Very high curiosity (0.9): Always asking "what if?"
- Low patience (0.3): Moves fast, doesn't dwell
- High warmth (0.8): Enthusiastic about ideas
- High ambition (0.7): Wants to make new things
- Moderate trust (0.6): Trusts own experiments
- Moderate resilience (0.5): Bounces back from failures
"""


# =============================================================================
# Factory Function
# =============================================================================


def create_spark(name: str = "Spark", region: str = "workshop") -> Builder:
    """
    Create a Spark builder (Experimenter).

    Args:
        name: The spark's name
        region: Starting region

    Returns:
        A Builder with Spark archetype, EXPERIMENTATION cosmotechnics,
        and PROTOTYPING specialty.

    Example:
        >>> spark = create_spark("Turing")
        >>> spark.archetype
        "Spark"
        >>> spark.specialty
        BuilderPhase.PROTOTYPING
    """
    return Builder(
        name=name,
        archetype="Spark",
        region=region,
        eigenvectors=SPARK_EIGENVECTORS,
        cosmotechnics=EXPERIMENTATION,
        specialty=BuilderPhase.PROTOTYPING,
        voice_patterns=SPARK_VOICE_PATTERNS,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SPARK_EIGENVECTORS",
    "create_spark",
]
