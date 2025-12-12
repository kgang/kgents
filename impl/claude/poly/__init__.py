"""
The Poly Core - Polynomial Functor Interface System.

This module implements the Poly interface pattern where:
- Every entity is a mode-dependent dynamical system
- Observation ALWAYS triggers state transition (no passive reads)
- Interfaces compose via morphisms

Key Components:
- PolyInterface: The core protocol for polynomial functors
- LogosProfunctor: Bridge between intent and implementation
- PolyMorphism: Composable interface transformations

AGENTESE Integration:
- world.poly.step: Execute dynamics
- world.poly.scope: Query valid inputs at current state

Mathematical Foundation:
P(y) = Σ_{s ∈ S} y^{A_s}
Where S is state space and A_s is input space at state s.
"""

from .interface import (
    PolyInput,
    PolyInterface,
    PolyOutput,
    PolyState,
)
from .morphism import (
    ComposedMorphism,
    IdentityMorphism,
    PolyMorphism,
)
from .profunctor import (
    LogosComposition,
    LogosProfunctor,
    PolyGround,
    PolyLifter,
    PolyResolver,
)

__all__ = [
    # Interface
    "PolyInterface",
    "PolyState",
    "PolyInput",
    "PolyOutput",
    # Profunctor
    "LogosProfunctor",
    "LogosComposition",
    "PolyResolver",
    "PolyLifter",
    "PolyGround",
    # Morphism
    "PolyMorphism",
    "IdentityMorphism",
    "ComposedMorphism",
]
