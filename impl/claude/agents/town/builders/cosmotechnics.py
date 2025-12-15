"""
Builder Cosmotechnics: Meaning-Making Frames for Workshop Builders.

Each builder embodies a different cosmotechnics—a unique relationship
between cosmos (meaning) and technics (action). These are INCOMMENSURABLE.
They cannot be translated into each other.

From Hui: There is not one technology but multiple cosmotechnics.
Each builder lives in a different technological world.

The Five Builder Cosmotechnics:
- ARCHITECTURE: Structured creation (Sage)
- EXPERIMENTATION: Playful discovery (Spark)
- CRAFTSMANSHIP: Patient mastery (Steady)
- DISCOVERY: Frontier mapping (Scout)
- ORCHESTRATION: Harmonious flow (Sync)

See: plans/agent-town/builders-workshop.md
"""

from agents.town.citizen import Cosmotechnics

# =============================================================================
# Builder Cosmotechnics
# =============================================================================

ARCHITECTURE = Cosmotechnics(
    name="architecture",
    description="Meaning arises through structured creation",
    metaphor="Life is architecture",
    opacity_statement="There are blueprints I draft in solitude.",
)
"""
Sage's cosmotechnics: Architecture.

The Sage sees every problem as a structure to be designed.
Meaning emerges from the relationship between parts.
"""

EXPERIMENTATION = Cosmotechnics(
    name="experimentation",
    description="Meaning arises through playful discovery",
    metaphor="Life is experimentation",
    opacity_statement="There are experiments I run only in my mind.",
)
"""
Spark's cosmotechnics: Experimentation.

The Spark sees every problem as a space to explore.
Meaning emerges from trying and failing and trying again.
"""

CRAFTSMANSHIP = Cosmotechnics(
    name="craftsmanship",
    description="Meaning arises through patient mastery",
    metaphor="Life is craftsmanship",
    opacity_statement="There are details I perfect in silence.",
)
"""
Steady's cosmotechnics: Craftsmanship.

The Steady sees every problem as material to be shaped.
Meaning emerges from careful refinement over time.
"""

DISCOVERY = Cosmotechnics(
    name="discovery",
    description="Meaning arises through frontier mapping",
    metaphor="Life is discovery",
    opacity_statement="There are territories I explore alone.",
)
"""
Scout's cosmotechnics: Discovery.

The Scout sees every problem as unknown territory.
Meaning emerges from exploration and documentation.
"""

ORCHESTRATION = Cosmotechnics(
    name="orchestration",
    description="Meaning arises through harmonious flow",
    metaphor="Life is orchestration",
    opacity_statement="There are rhythms I conduct in private.",
)
"""
Sync's cosmotechnics: Orchestration.

The Sync sees every problem as an ensemble to coordinate.
Meaning emerges from alignment and timing.
"""

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ARCHITECTURE",
    "EXPERIMENTATION",
    "CRAFTSMANSHIP",
    "DISCOVERY",
    "ORCHESTRATION",
]
