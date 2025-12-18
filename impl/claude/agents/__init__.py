"""
kgents Agent Genera — Batteries Included.

Each letter represents a distinct agent genus:
- A-gents: Abstract architectures + Art/Creativity (the skeleton)
- B-gents: Bio/Scientific discovery
- C-gents: Category theory (composability)
- D-gents: Data agents (persistence substrate, WHERE state lives)
- K-gent: Kent simulacra
- S-gents: State agents (state threading, HOW state flows)
- T-gents: Testing agents (verification, perturbation, observation)
- U-gents: Utility agents (tools, MCP, execution)

Archived (see agents/_archived/):
- H-gents: Hegel/Jung/Lacan (dialectics) - archived 2025-12-16
- Q-gent: Quartermaster (K8s jobs) - archived 2025-12-16
- R-gents: Refinery (DSPy optimization) - archived 2025-12-16
- Psi-gent: Metaphor engine - archived 2025-12-16

Quick Start:
    >>> from agents import Agent, Kappa, Capability
    >>> from agents import Maybe, Just, Nothing, Flux
    >>>
    >>> @Capability.Stateful(schema=MyState)
    ... class MyAgent(Agent[str, str]):
    ...     async def invoke(self, input: str) -> str:
    ...         return f"Hello, {input}!"

See agents.examples for runnable demonstrations.
"""

# Submodules (for qualified access)
# ─────────────────────────────────────────────────────────────────────────────
# The Skeleton: Agent Base Class
# ─────────────────────────────────────────────────────────────────────────────
from agents.poly.types import Agent, ComposedAgent

from . import a, b, c, d, k, s, t, u

# ─────────────────────────────────────────────────────────────────────────────
# Alethic Architecture: Halo Capability Protocol
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Alethic Algebra: Universal Functor Protocol
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Quick Agent Creation
# ─────────────────────────────────────────────────────────────────────────────
from .a import (
    # Archetypes (pre-packaged Halos)
    Archetype,
    # Capability decorators
    Capability,
    Delta,  # Data-focused: Stateful + Observable
    FunctionAgent,  # The underlying type
    FunctorRegistry,
    Kappa,  # Full stack: Stateful + Soulful + Observable + Streamable
    Lambda,  # Minimal: Observable only
    UniversalFunctor,
    agent,  # @agent decorator
    compose_functors,
    get_halo,
    has_capability,
    pipeline,  # Compose multiple agents
    verify_functor,
)

# ─────────────────────────────────────────────────────────────────────────────
# C-gent: Composition Primitives
# ─────────────────────────────────────────────────────────────────────────────
from .c import (
    # Either: Success or error
    Either,
    EitherFunctor,
    Just,
    Left,
    # Maybe: Optional values
    Maybe,
    MaybeFunctor,
    Nothing,
    Right,
    # Conditional composition
    branch,
    fan_out,
    # Parallel composition
    parallel,
    race,
    switch,
)

# ─────────────────────────────────────────────────────────────────────────────
# Flux: Stream Processing
# ─────────────────────────────────────────────────────────────────────────────
from .flux import (
    Flux,
    FluxAgent,
    FluxConfig,
    FluxFunctor,
    lift as flux_lift,
    pipeline as flux_pipeline,
)

# ─────────────────────────────────────────────────────────────────────────────
# K-gent: Soul / Persona
# ─────────────────────────────────────────────────────────────────────────────
from .k import (
    Soul,
    SoulFunctor,
    soul_lift,
)

# ─────────────────────────────────────────────────────────────────────────────
# S-gent: State Threading
# ─────────────────────────────────────────────────────────────────────────────
from .s import (
    MemoryStateBackend,
    StateBackend,
    StateConfig,
    StatefulAgent,
    StateFunctor,
)

__all__ = [
    # Submodules
    "a",
    "b",
    "c",
    "d",
    "k",
    "s",
    "t",
    "u",
    # The Skeleton
    "Agent",
    "ComposedAgent",
    # Alethic Architecture
    "Capability",
    "get_halo",
    "has_capability",
    "Archetype",
    "Kappa",
    "Lambda",
    "Delta",
    # Alethic Algebra
    "UniversalFunctor",
    "FunctorRegistry",
    "compose_functors",
    "verify_functor",
    # Quick Agent Creation
    "agent",
    "pipeline",
    "FunctionAgent",
    # C-gent: Composition
    "Maybe",
    "Just",
    "Nothing",
    "MaybeFunctor",
    "Either",
    "Left",
    "Right",
    "EitherFunctor",
    "parallel",
    "fan_out",
    "race",
    "branch",
    "switch",
    # Flux: Streams
    "Flux",
    "FluxAgent",
    "FluxConfig",
    "FluxFunctor",
    "flux_lift",
    "flux_pipeline",
    # K-gent: Soul
    "Soul",
    "SoulFunctor",
    "soul_lift",
    # S-gent: State
    "StateBackend",
    "StateConfig",
    "StateFunctor",
    "StatefulAgent",
    "MemoryStateBackend",
]
