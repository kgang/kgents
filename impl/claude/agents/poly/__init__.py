"""
Poly: Polynomial Agent Infrastructure.

Agents as dynamical systems based on Spivak's polynomial functors.

This module provides:
- PolyAgent: The core polynomial agent type
- Primitives: 17 atomic polynomial agents
- Composition: Sequential and parallel wiring

The key insight: Agent[A, B] ≅ A → B is a lie.
PolyAgent[S, A, B] captures state-dependent behavior:
    P(y) = Σ_{s ∈ positions} y^{directions(s)}

See: plans/ideas/impl/meta-construction.md
"""

from .primitives import (
    # Types - Bootstrap
    Antithesis,
    Claim,
    ContradictState,
    Definition,
    FixState,
    GroundState,
    JudgeState,
    SublateState,
    Spec,
    Synthesis,
    Thesis,
    Verdict,
    # Types - Perception
    Handle,
    Manifestation,
    Trace,
    Umwelt,
    WitnessState,
    # Types - Entropy
    EntropyGrant,
    EntropyRequest,
    Offering,
    SipState,
    TitheState,
    # Types - Memory (D-gent)
    ForgetState,
    Memory,
    MemoryResult,
    RememberState,
    # Types - Teleological (E-gent, N-gent)
    Evolution,
    EvolveState,
    NarrateState,
    Organism,
    Story,
    # Primitives - Bootstrap (7)
    COMPOSE,
    CONTRADICT,
    FIX,
    GROUND,
    ID,
    JUDGE,
    SUBLATE,
    # Primitives - Perception (3)
    LENS,
    MANIFEST,
    WITNESS,
    # Primitives - Entropy (3)
    DEFINE,
    SIP,
    TITHE,
    # Primitives - Memory (2)
    FORGET,
    REMEMBER,
    # Primitives - Teleological (2)
    EVOLVE,
    NARRATE,
    # Registry
    PRIMITIVES,
    all_primitives,
    get_primitive,
    primitive_names,
)
from .protocol import (
    # Core
    PolyAgent,
    PolyAgentProtocol,
    WiringDiagram,
    # Constructors
    constant,
    from_function,
    identity,
    # Composition
    parallel,
    sequential,
    stateful,
)

__all__ = [
    # Protocol
    "PolyAgentProtocol",
    "PolyAgent",
    "WiringDiagram",
    # Constructors
    "identity",
    "constant",
    "stateful",
    "from_function",
    # Composition
    "sequential",
    "parallel",
    # Types - Bootstrap
    "GroundState",
    "JudgeState",
    "ContradictState",
    "SublateState",
    "FixState",
    "Claim",
    "Verdict",
    "Thesis",
    "Antithesis",
    "Synthesis",
    # Types - Perception
    "WitnessState",
    "Handle",
    "Umwelt",
    "Manifestation",
    "Trace",
    # Types - Entropy
    "SipState",
    "TitheState",
    "EntropyRequest",
    "EntropyGrant",
    "Offering",
    "Spec",
    "Definition",
    # Types - Memory (D-gent)
    "RememberState",
    "ForgetState",
    "Memory",
    "MemoryResult",
    # Types - Teleological (E-gent, N-gent)
    "EvolveState",
    "NarrateState",
    "Organism",
    "Evolution",
    "Story",
    # Primitives - Bootstrap (7)
    "ID",
    "GROUND",
    "JUDGE",
    "CONTRADICT",
    "SUBLATE",
    "COMPOSE",
    "FIX",
    # Primitives - Perception (3)
    "MANIFEST",
    "WITNESS",
    "LENS",
    # Primitives - Entropy (3)
    "SIP",
    "TITHE",
    "DEFINE",
    # Primitives - Memory (2)
    "REMEMBER",
    "FORGET",
    # Primitives - Teleological (2)
    "EVOLVE",
    "NARRATE",
    # Registry
    "PRIMITIVES",
    "get_primitive",
    "all_primitives",
    "primitive_names",
]
