"""
kgents Agent Genera — Batteries Included.

Each letter represents a distinct agent genus:
- A-gents: Abstract architectures + Art/Creativity (the skeleton)
- B-gents: Bio/Scientific discovery
- C-gents: Category theory (composability)
- H-gents: Hegel/Jung/Lacan (dialectics, psyche)
- K-gent: Kent simulacra
- T-gents: Testing agents (verification, perturbation, observation)
- U-gents: Utility agents (tools, MCP, execution)

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
from bootstrap.types import Agent, ComposedAgent

from . import a, b, c, h, k, t, u

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
)
from .flux import (
    lift as flux_lift,
)
from .flux import (
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

__all__ = [
    # Submodules
    "a",
    "b",
    "c",
    "h",
    "k",
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
]
