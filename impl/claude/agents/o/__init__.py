"""
O-gent: The Observation Layer

After radical refinement (2025-12), O-gent provides the categorical
observation layer that lifts agents into observability:

1. Observer Functor - mathematical abstraction for observation
2. Bootstrap Witness - law verification for categorical primitives

For runtime observation, use the Witness protocol directly.
For Brain/Cortex observation, import from services.brain.cortex_observer.
"""

from .bootstrap_witness import (
    AgentExistenceResult,
    BootstrapAgent,
    BootstrapVerificationResult,
    BootstrapWitness,
    ComposedAgent,
    CompositionLawResult,
    IdentityAgent,
    IdentityLawResult,
    TestAgent,
    Verdict,
)
from .observer import (
    Agent,
    BaseObserver,
    ObservationContext,
    ObservationResult,
    ObservationStatus,
    Observer,
    ObserverFunctor,
    ProprioceptiveWrapper,
    observe,
)

__all__ = [
    # Observer Functor
    "Agent",
    "Observer",
    "BaseObserver",
    "ObservationContext",
    "ObservationResult",
    "ObservationStatus",
    "ObserverFunctor",
    "ProprioceptiveWrapper",
    "observe",
    # Bootstrap Witness
    "BootstrapWitness",
    "IdentityAgent",
    "TestAgent",
    "ComposedAgent",
    # Bootstrap Results
    "Verdict",
    "BootstrapAgent",
    "AgentExistenceResult",
    "IdentityLawResult",
    "CompositionLawResult",
    "BootstrapVerificationResult",
]
