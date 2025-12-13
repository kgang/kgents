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
    # Primitives - Bootstrap (7)
    COMPOSE,
    CONTRADICT,
    # Primitives - Entropy (3)
    DEFINE,
    # Primitives - Teleological (2)
    EVOLVE,
    FIX,
    # Primitives - Memory (2)
    FORGET,
    GROUND,
    ID,
    JUDGE,
    # Primitives - Perception (3)
    LENS,
    MANIFEST,
    NARRATE,
    # Registry
    PRIMITIVES,
    REMEMBER,
    SIP,
    SUBLATE,
    TITHE,
    WITNESS,
    # Types - Bootstrap
    Antithesis,
    Claim,
    ContradictState,
    Definition,
    # Types - Entropy
    EntropyGrant,
    EntropyRequest,
    # Types - Teleological (E-gent, N-gent)
    Evolution,
    EvolveState,
    FixState,
    # Types - Memory (D-gent)
    ForgetState,
    GroundState,
    # Types - Perception
    Handle,
    JudgeState,
    Manifestation,
    Memory,
    MemoryResult,
    NarrateState,
    Offering,
    Organism,
    RememberState,
    SipState,
    Spec,
    Story,
    SublateState,
    Synthesis,
    Thesis,
    TitheState,
    Trace,
    Umwelt,
    Verdict,
    WitnessState,
    all_primitives,
    get_primitive,
    primitive_names,
)
from .protocol import (
    # Core
    PolyAgent,
    PolyAgentProtocol,
    # Deprecation Sugar
    StatelessAgent,
    WiringDiagram,
    # Constructors
    constant,
    from_bootstrap_agent,
    from_function,
    identity,
    # Composition
    parallel,
    sequential,
    stateful,
    to_bootstrap_agent,
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
    # Deprecation Sugar
    "StatelessAgent",
    "to_bootstrap_agent",
    "from_bootstrap_agent",
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
