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

__all__ = [
    # Core
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
]
