"""
Poly: Polynomial Agent Infrastructure.

Agents as dynamical systems based on Spivak's polynomial functors.

This module provides:
- PolyAgent: The core polynomial agent type
- Agent[A, B]: Bootstrap agent type (async invoke)
- Primitives: 17 atomic polynomial agents
- Composition: Sequential and parallel wiring
- Types: Core domain types from bootstrap

The key insight: Agent[A, B] ≅ A → B is a lie.
PolyAgent[S, A, B] captures state-dependent behavior:
    P(y) = Σ_{s ∈ positions} y^{directions(s)}

Migration: 2025-12-16
- Bootstrap types migrated here from impl/claude/bootstrap/types.py
- Bootstrap module re-exports from here for backward compatibility

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
    # Types - Teleological (Evolve, Narrate)
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

# Bootstrap types (migrated from bootstrap/types.py)
from .types import (
    VOID,
    Agent,
    AgentProtocol,
    ComposedAgent,
    ContradictInput,
    ContradictResult,
    Err,
    Facts,
    FixConfig,
    FixResult,
    HoldTension,
    JudgeInput,
    Ok,
    PartialVerdict,
    PersonaSeed,
    Principles,
    Result,
    SublateInput,
    SublateResult,
    Synthesis as BootstrapSynthesis,
    Tension,
    TensionMode,
    Verdict as BootstrapVerdict,
    VerdictType,
    Void,
    WorldSeed,
    err,
    ok,
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
    # Types - Teleological (Evolve, Narrate)
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
    # Bootstrap Types (migrated from bootstrap/types.py)
    "Agent",
    "AgentProtocol",
    "ComposedAgent",
    "Result",
    "Ok",
    "Err",
    "ok",
    "err",
    "TensionMode",
    "Tension",
    "BootstrapSynthesis",
    "HoldTension",
    "VerdictType",
    "PartialVerdict",
    "BootstrapVerdict",
    "Principles",
    "PersonaSeed",
    "WorldSeed",
    "Facts",
    "FixConfig",
    "FixResult",
    "ContradictInput",
    "ContradictResult",
    "SublateInput",
    "SublateResult",
    "JudgeInput",
    "Void",
    "VOID",
]
