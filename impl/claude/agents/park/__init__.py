"""
Punchdrunk Park: Immersive Simulation Agents.

> *"Westworld-like simulation where citizens can say no."*

This module provides the director and pacing infrastructure for
Punchdrunk Park experiences, building on top of Agent Town's
INHABIT mode.

Key Components:
- DirectorAgent: Monitors session pace, injects serendipity
- PacingMetrics: Tracks session pacing and tension
- SerendipityInjection: Events injected via void.entropy
- DialogueMask: Character masks with eigenvector transforms (Wave 3)
- ParkDomainBridge: Integration with Domain simulation (Wave 3)

Philosophy:
    "Collaboration > control. Citizen refusal is core feature, not bug."

    The director is NOT a game master who controls outcomes.
    The director is a gentle hand on the entropy dial.

See: plans/core-apps/punchdrunk-park.md
"""

from agents.park.director import (
    DIRECTOR_POLYNOMIAL,
    DifficultyAdjustment,
    DirectorAgent,
    DirectorConfig,
    DirectorPhase,
    InjectionDecision,
    PacingMetrics,
    SerendipityInjection,
    TensionEscalation,
    create_director,
)
from agents.park.domain_bridge import (
    IntegratedScenarioConfig,
    IntegratedScenarioState,
    IntegratedScenarioType,
    ParkDomainBridge,
    TimerConfig,
    create_compliance_drill,
    create_data_breach_practice,
    create_service_outage_practice,
)
from agents.park.masks import (
    ARCHITECT_MASK,
    CHILD_MASK,
    DREAMER_MASK,
    HEALER_MASK,
    MASK_DECK,
    SAGE_MASK,
    SKEPTIC_MASK,
    TRICKSTER_MASK,
    WARRIOR_MASK,
    DialogueMask,
    EigenvectorTransform,
    MaskArchetype,
    MaskedSessionState,
    create_masked_state,
    get_mask,
    list_masks,
)

__all__ = [
    # Core Director
    "DirectorAgent",
    "DirectorPhase",
    "DirectorConfig",
    # Metrics and Events
    "PacingMetrics",
    "SerendipityInjection",
    "TensionEscalation",
    "DifficultyAdjustment",
    "InjectionDecision",
    # Polynomial
    "DIRECTOR_POLYNOMIAL",
    # Factory
    "create_director",
    # Wave 3: Domain Bridge
    "ParkDomainBridge",
    "IntegratedScenarioType",
    "IntegratedScenarioConfig",
    "IntegratedScenarioState",
    "TimerConfig",
    "create_data_breach_practice",
    "create_service_outage_practice",
    "create_compliance_drill",
    # Wave 3: Dialogue Masks
    "DialogueMask",
    "MaskArchetype",
    "EigenvectorTransform",
    "MaskedSessionState",
    "MASK_DECK",
    "TRICKSTER_MASK",
    "DREAMER_MASK",
    "SKEPTIC_MASK",
    "ARCHITECT_MASK",
    "CHILD_MASK",
    "SAGE_MASK",
    "WARRIOR_MASK",
    "HEALER_MASK",
    "get_mask",
    "list_masks",
    "create_masked_state",
]
