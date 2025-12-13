"""
A-gents: Abstract Architectures + Art/Creativity

A-gents provide:
- The agent skeleton (what every agent MUST be)
- Creativity-focused agents for idea expansion
- Bootstrap verification (BootstrapWitness)
- Category-theoretic protocols (Morphism, Functor)
- Agent factory (AgentFactory)
- Self-describing agents (GroundedSkeleton)
- **Alethic Architecture**: Halo capability protocol + Archetypes
- **Alethic Agent**: Polynomial agent for truth-seeking (Phase 3 migration)

The key insight of A-gents: Agent[A, B] from bootstrap IS the skeleton.
AbstractAgent is just an alias for semantic clarity.

For richer metadata, use AgentMeta (optional).

## The Alethic Architecture

The Halo system provides declarative capabilities:
- Nucleus: Pure logic (what the agent does)
- Halo: Declarative capabilities (what the agent could become)
- Archetype: Pre-packaged Halo for common patterns
- Projector: Target-specific compilation (how the agent manifests)

Example:
    >>> @Capability.Stateful(schema=MyMemory)
    ... @Capability.Soulful(persona="Kent")
    ... class MyAgent(Agent[str, str]):
    ...     async def invoke(self, input: str) -> str:
    ...         return f"Hello, {input}"

Or using archetypes:
    >>> class MyService(Kappa[Request, Response]):
    ...     async def invoke(self, req: Request) -> Response:
    ...         return process(req)

## Alethic Agent (Polynomial)

The AlethicAgent models truth-seeking as a polynomial state machine:
- GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING

Example:
    >>> agent = AlethicAgent()
    >>> response = await agent.reason(Query(claim="The sky is blue"))
    >>> print(response.verdict.accepted)

See: plans/architecture/alethic.md, plans/architecture/polyfunctor.md
"""

# Alethic Agent: Polynomial truth-seeking (Phase 3 migration)
from .alethic import (
    # Polynomial Agent
    ALETHIC_AGENT,
    # Wrapper
    AlethicAgent,
    # Types
    AlethicResponse,
    # State Machine
    AlethicState,
    DeliberationResult,
    Evidence,
    Query,
    alethic_directions,
    alethic_transition,
)

# Alethic Architecture: Genus Archetypes
from .archetypes import (
    # Base
    Archetype,
    # Standard Archetypes
    Delta,
    Kappa,
    Lambda,
    # Utilities
    get_archetype,
    is_archetype_instance,
)
from .creativity import (
    # Agent
    CreativityCoach,
    CreativityInput,
    # Types
    CreativityMode,
    CreativityResponse,
    Persona,
    # Convenience functions
    creativity_coach,
    philosophical_coach,
    playful_coach,
    provocative_coach,
)

# Alethic Algebra: Universal Functor Protocol
from .functor import (
    # Verification
    FunctorLawResult,
    # Core Protocol
    FunctorRegistry,
    FunctorVerificationReport,
    Liftable,
    Pointed,
    UniversalFunctor,
    # Combinators
    compose_functors,
    identity_functor,
    verify_composition_law,
    verify_functor,
    verify_identity_law,
)
from .halo import (
    HALO_ATTR,
    # Base
    Capability,
    CapabilityBase,
    # Capability types
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    # Introspection
    get_capability,
    get_halo,
    get_own_halo,
    has_capability,
    inherit_halo,
    merge_halos,
)

# Quick agent creation
from .quick import (
    FunctionAgent,
    agent,
    pipeline,
)
from .skeleton import (
    # The skeleton (re-exported from bootstrap)
    AbstractAgent,
    AgentBehavior,
    AgentFactory,
    AgentIdentity,
    AgentInterface,
    # Optional metadata
    AgentMeta,
    # Phase 3: AgentFactory
    AgentSpec,
    AutopoieticAgent,
    # Phase 1: BootstrapWitness
    BootstrapVerificationResult,
    BootstrapWitness,
    FactoryAgent,
    Functor,
    # Phase 4: GroundedSkeleton
    GroundedSkeleton,
    # Phase 2: Category-Theoretic Protocols
    Morphism,
    check_composition,
    get_codomain,
    get_domain,
    get_meta,
    # Utilities
    has_meta,
    verify_composition_types,
)

__all__ = [
    # Core skeleton
    "AbstractAgent",
    # Metadata (optional)
    "AgentMeta",
    "AgentIdentity",
    "AgentInterface",
    "AgentBehavior",
    # Utilities
    "has_meta",
    "get_meta",
    "check_composition",
    # Phase 1: BootstrapWitness
    "BootstrapVerificationResult",
    "BootstrapWitness",
    # Phase 2: Category-Theoretic Protocols
    "Morphism",
    "Functor",
    "get_domain",
    "get_codomain",
    "verify_composition_types",
    # Phase 3: AgentFactory
    "AgentSpec",
    "AgentFactory",
    "FactoryAgent",
    # Phase 4: GroundedSkeleton
    "GroundedSkeleton",
    "AutopoieticAgent",
    # Creativity Coach
    "CreativityMode",
    "CreativityInput",
    "CreativityResponse",
    "Persona",
    "CreativityCoach",
    "creativity_coach",
    "playful_coach",
    "philosophical_coach",
    "provocative_coach",
    # Alethic Architecture: Halo Capability Protocol
    "Capability",
    "CapabilityBase",
    "HALO_ATTR",
    "StatefulCapability",
    "SoulfulCapability",
    "ObservableCapability",
    "StreamableCapability",
    "get_halo",
    "get_own_halo",
    "has_capability",
    "get_capability",
    "merge_halos",
    "inherit_halo",
    # Alethic Algebra: Universal Functor Protocol
    "UniversalFunctor",
    "Liftable",
    "Pointed",
    "FunctorRegistry",
    "FunctorLawResult",
    "FunctorVerificationReport",
    "verify_identity_law",
    "verify_composition_law",
    "verify_functor",
    "compose_functors",
    "identity_functor",
    # Alethic Architecture: Genus Archetypes
    "Archetype",
    "Kappa",
    "Lambda",
    "Delta",
    "get_archetype",
    "is_archetype_instance",
    # Alethic Agent: Polynomial truth-seeking (Phase 3 Polyfunctor)
    "AlethicState",
    "Query",
    "Evidence",
    "DeliberationResult",
    "AlethicResponse",
    "ALETHIC_AGENT",
    "alethic_directions",
    "alethic_transition",
    "AlethicAgent",
    # Quick agent creation
    "FunctionAgent",
    "agent",
    "pipeline",
]
