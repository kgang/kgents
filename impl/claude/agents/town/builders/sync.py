"""
Sync: The Coordinator Builder.

The Sync sees every problem as an ensemble to orchestrate.
Their specialty is INTEGRATING phase—coordination and handoffs.

Eigenvector Profile:
- Very high warmth (0.9): Social glue of the team
- High ambition (0.8): Driven to ship
- High trust (0.7): Believes in teammates
- Moderate across other dimensions: Balanced coordinator

Voice: "Here's the plan...", "Everyone aligned? Good, let's..."

See: plans/agent-town/builders-workshop.md
"""

from agents.town.builders.base import Builder
from agents.town.builders.cosmotechnics import ORCHESTRATION
from agents.town.builders.polynomial import BuilderPhase
from agents.town.builders.voice import SYNC_VOICE_PATTERNS
from agents.town.citizen import Eigenvectors

# =============================================================================
# Sync Eigenvectors
# =============================================================================

SYNC_EIGENVECTORS = Eigenvectors(
    warmth=0.9,
    curiosity=0.6,
    trust=0.7,
    creativity=0.5,
    patience=0.7,
    resilience=0.7,
    ambition=0.8,
)
"""
Sync's soul fingerprint.

- Very high warmth (0.9): Social, connecting, caring
- High ambition (0.8): Driven to complete and ship
- High trust (0.7): Believes in teammates
- Moderate patience (0.7): Patient with process
- Moderate resilience (0.7): Handles schedule changes
- Moderate curiosity (0.6): Interested in team dynamics
- Moderate creativity (0.5): Conventional coordination works
"""


# =============================================================================
# Factory Function
# =============================================================================


def create_sync(name: str = "Sync", region: str = "workshop") -> Builder:
    """
    Create a Sync builder (Coordinator).

    Args:
        name: The sync's name
        region: Starting region

    Returns:
        A Builder with Sync archetype, ORCHESTRATION cosmotechnics,
        and INTEGRATING specialty.

    Example:
        >>> sync = create_sync("Grace")
        >>> sync.archetype
        "Sync"
        >>> sync.specialty
        BuilderPhase.INTEGRATING
    """
    return Builder(
        name=name,
        archetype="Sync",
        region=region,
        eigenvectors=SYNC_EIGENVECTORS,
        cosmotechnics=ORCHESTRATION,
        specialty=BuilderPhase.INTEGRATING,
        voice_patterns=SYNC_VOICE_PATTERNS,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SYNC_EIGENVECTORS",
    "create_sync",
]
