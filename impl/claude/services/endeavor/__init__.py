"""
Endeavor Service: Axiom discovery and pilot bootstrapping for tangible endeavors.

This module provides:
- AxiomDiscoveryService: Guided dialogue to discover endeavor axioms
- PilotBootstrapService: Bootstrap custom pilots from axioms
- EndeavorAxioms: Structured representation of discovered axioms

The Self-Reflective OS Pattern:
- Endeavors are user intentions that need tangible form
- Axioms ground the endeavor in verifiable success criteria
- Pilots are the implementation vehicles

AGENTESE: self.tangibility.endeavor

Example:
    from services.endeavor import AxiomDiscoveryService, EndeavorAxioms

    discovery = AxiomDiscoveryService()
    session = await discovery.start_discovery("I want to build a daily journaling habit")

    # Process user responses through 5-turn dialogue
    turn = await discovery.process_turn(session.session_id, "I want to feel more present")

    # Complete discovery
    axioms = await discovery.complete_discovery(session.session_id)
    print(axioms.success_definition)

See: pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
"""

from .bootstrap import (
    CustomPilot,
    PilotBootstrapService,
    PilotMatch,
    WitnessConfig,
    get_pilot_bootstrap_service,
)
from .discovery import (
    AxiomDiscoveryService,
    DiscoveryPhase,
    DiscoverySession,
    DiscoveryTurn,
    EndeavorAxioms,
    get_axiom_discovery_service,
)

__all__ = [
    # Discovery
    "AxiomDiscoveryService",
    "DiscoverySession",
    "DiscoveryTurn",
    "DiscoveryPhase",
    "EndeavorAxioms",
    "get_axiom_discovery_service",
    # Bootstrap
    "PilotBootstrapService",
    "PilotMatch",
    "CustomPilot",
    "WitnessConfig",
    "get_pilot_bootstrap_service",
]
