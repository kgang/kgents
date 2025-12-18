"""
Agent Town: A Civilizational Engine for Agent Societies.

This module implements the Agent Town MPP (Minimal Playable Prototype),
a compositional multi-agent simulation where citizens interact through
an operad-based grammar.

Core Components:
- CitizenPolynomial: State machine for citizen behavior
- TownOperad: Interaction grammar extending SOUL_OPERAD
- Citizen: The citizen entity with memory and eigenvectors
- TownEnvironment: The mesh topology of regions
- TownFlux: The simulation loop

Philosophical Substrate:
- Archaeological (Porras-Kim): Citizens are excavated, not created
- Hyperobjectival (Morton): Citizens are distributed in time/relation
- Intra-active (Barad): Citizens emerge through observation
- Opaque (Glissant): Irreducible unknowable core
- Cosmotechnical (Hui): Unique moral-cosmic-technical unity
- Accursed (Bataille): Surplus must be spent gloriously

See: spec/town/metaphysics.md
"""

from __future__ import annotations

from .citizen import Citizen, Eigenvectors
from .environment import Region, TownEnvironment
from .flux import TownEvent, TownFlux
from .operad import TOWN_OPERAD, create_town_operad
from .polynomial import (
    CITIZEN_POLYNOMIAL,
    CitizenInput,
    CitizenOutput,
    CitizenPhase,
    citizen_directions,
    citizen_transition,
)
from .workshop import (
    WorkshopArtifact,
    WorkshopEnvironment,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopPhase,
    WorkshopPlan,
    WorkshopState,
    WorkshopTask,
    create_workshop,
    create_workshop_with_builders,
)

__all__ = [
    # Polynomial
    "CITIZEN_POLYNOMIAL",
    "CitizenPhase",
    "CitizenInput",
    "CitizenOutput",
    "citizen_directions",
    "citizen_transition",
    # Citizen
    "Citizen",
    "Eigenvectors",
    # Environment
    "TownEnvironment",
    "Region",
    # Operad
    "TOWN_OPERAD",
    "create_town_operad",
    # Flux
    "TownFlux",
    "TownEvent",
    # Workshop
    "WorkshopEnvironment",
    "WorkshopPhase",
    "WorkshopEventType",
    "WorkshopEvent",
    "WorkshopTask",
    "WorkshopArtifact",
    "WorkshopPlan",
    "WorkshopState",
    "create_workshop",
    "create_workshop_with_builders",
]
