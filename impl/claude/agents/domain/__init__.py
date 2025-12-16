"""
Domain: Enterprise Domain Simulation.

Agent Town configured for specific enterprise verticals with:
- Domain polynomials (state machines for domain entities)
- Domain archetypes (role-specific citizens)
- Compliance timers (GDPR 72h, SEC 4-day, etc.)
- Inject framework (runtime crisis escalation)

Available verticals:
- drills: Crisis simulation drills (service outage, data breach)
- (future) urban: Urban planning simulation
- (future) economic: Economic policy simulation

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

from .drills import (
    CRISIS_ARCHETYPE_SPECS,
    # Polynomial
    CRISIS_POLYNOMIAL,
    DATA_BREACH_SPEC,
    SERVICE_OUTAGE_SPEC,
    # Archetypes
    CrisisArchetype,
    CrisisArchetypeSpec,
    CrisisInput,
    CrisisOutput,
    CrisisPhase,
    DrillDifficulty,
    DrillInstance,
    DrillStatus,
    # Templates
    DrillType,
    InjectSequence,
    InjectStatus,
    # Injects
    InjectType,
    TimerState,
    TimerStatus,
    # Timers
    TimerType,
    create_crisis_citizen,
    create_data_breach_drill,
    create_data_breach_injects,
    create_data_breach_team,
    create_drill,
    create_gdpr_timer,
    create_service_outage_drill,
    create_service_outage_injects,
    create_service_outage_team,
    format_countdown,
    list_drill_types,
)

__all__ = [
    # Polynomial
    "CRISIS_POLYNOMIAL",
    "CrisisInput",
    "CrisisOutput",
    "CrisisPhase",
    # Archetypes
    "CrisisArchetype",
    "CrisisArchetypeSpec",
    "CRISIS_ARCHETYPE_SPECS",
    "create_crisis_citizen",
    "create_data_breach_team",
    "create_service_outage_team",
    # Timers
    "TimerType",
    "TimerStatus",
    "TimerState",
    "create_gdpr_timer",
    "format_countdown",
    # Injects
    "InjectType",
    "InjectStatus",
    "InjectSequence",
    "create_service_outage_injects",
    "create_data_breach_injects",
    # Templates
    "DrillType",
    "DrillDifficulty",
    "DrillStatus",
    "DrillInstance",
    "SERVICE_OUTAGE_SPEC",
    "DATA_BREACH_SPEC",
    "create_service_outage_drill",
    "create_data_breach_drill",
    "create_drill",
    "list_drill_types",
]
