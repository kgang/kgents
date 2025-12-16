"""
Workshop: Orchestration and composition for Tiny Atelier.

The workshop coordinates:
- Commission routing to artisans
- EventBus for streaming
- Collaboration pipelines
- Async commission queue
"""

from agents.atelier.workshop.collaboration import Collaboration, CollaborationMode
from agents.atelier.workshop.commission import CommissionQueue
from agents.atelier.workshop.operad import ATELIER_OPERAD, CompositionLaw, Operation
from agents.atelier.workshop.orchestrator import Workshop, WorkshopFlux, get_workshop

__all__ = [
    # Operad
    "ATELIER_OPERAD",
    "CompositionLaw",
    "Operation",
    # Collaboration
    "Collaboration",
    "CollaborationMode",
    # Queue
    "CommissionQueue",
    # Orchestrator
    "Workshop",
    "WorkshopFlux",
    "get_workshop",
]
