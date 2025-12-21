"""
A-gents: Alethic Architecture

The "A" stands for **Aletheia** (truth) and **Architecture**.

A-gents provide the **truth-preserving** foundation for all agents:

1. **Skeleton**: The minimal agent contract (identity, interface, behavior)
2. **Halo**: Declarative capabilities (@Capability.* decorators)
3. **Archetypes**: Pre-packaged patterns (Kappa, Lambda, Delta)
4. **Alethic Agent**: Polynomial state machine for truth-seeking
5. **Functor Protocol**: Universal lifting with law verification

## The Nucleus-Halo-Projector Triad

```
Nucleus    → Pure Agent[A, B] logic (what it does)
Halo       → @Capability.* decorators (what it could become)
Projector  → Target-specific compilation (how it manifests)
```

## Alethic Agent (Polynomial)

The AlethicAgent models truth-seeking as a polynomial state machine:
    GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING

Example:
    >>> from agents.a import AlethicAgent, Query
    >>> agent = AlethicAgent()
    >>> response = await agent.reason(Query(claim="The sky is blue"))
    >>> print(response.verdict.accepted)

## Archetypes

    >>> from agents.a import Kappa
    >>> class MyService(Kappa[Request, Response]):
    ...     async def invoke(self, req: Request) -> Response:
    ...         return process(req)

See: spec/a-gents/README.md, spec/a-gents/alethic.md
"""

# =============================================================================
# ALETHIC ARCHITECTURE: Core Components
# =============================================================================

# Alethic Agent: Polynomial truth-seeking
from .alethic import (
    ALETHIC_AGENT,
    AlethicAgent,
    AlethicResponse,
    AlethicState,
    DeliberationResult,
    Evidence,
    Query,
    alethic_directions,
    alethic_transition,
)

# Archetypes: Pre-packaged Halos
from .archetypes import (
    Archetype,
    Delta,
    Kappa,
    Lambda,
    get_archetype,
    is_archetype_instance,
)

# =============================================================================
# LEGACY: Creativity Coach (deprecated from A-gent core)
# These remain for backwards compatibility but are NOT part of Alethic Architecture.
# Consider moving to services/muse/ in a future refactor.
# =============================================================================
from .creativity import (
    CreativityCoach,
    CreativityInput,
    CreativityMode,
    CreativityResponse,
    Persona,
    creativity_coach,
    philosophical_coach,
    playful_coach,
    provocative_coach,
)

# Functor Protocol: Universal lifting with law verification
from .functor import (
    FunctorLawResult,
    FunctorRegistry,
    FunctorVerificationReport,
    Liftable,
    Pointed,
    UniversalFunctor,
    compose_functors,
    identity_functor,
    verify_composition_law,
    verify_functor,
    verify_identity_law,
)

# Halo: Declarative capabilities
from .halo import (
    HALO_ATTR,
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
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

# Skeleton: Minimal agent contract
from .skeleton import (
    AbstractAgent,
    AgentBehavior,
    AgentFactory,
    AgentIdentity,
    AgentInterface,
    AgentMeta,
    AgentSpec,
    AutopoieticAgent,
    BootstrapVerificationResult,
    BootstrapWitness,
    FactoryAgent,
    Functor,
    GroundedSkeleton,
    Morphism,
    check_composition,
    get_codomain,
    get_domain,
    get_meta,
    has_meta,
    verify_composition_types,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # =========================================================================
    # ALETHIC ARCHITECTURE: Primary Exports
    # =========================================================================
    # Alethic Agent (Polynomial truth-seeking)
    "AlethicState",
    "Query",
    "Evidence",
    "DeliberationResult",
    "AlethicResponse",
    "ALETHIC_AGENT",
    "alethic_directions",
    "alethic_transition",
    "AlethicAgent",
    # Skeleton (minimal agent contract)
    "AbstractAgent",
    "AgentMeta",
    "AgentIdentity",
    "AgentInterface",
    "AgentBehavior",
    "has_meta",
    "get_meta",
    "check_composition",
    # Bootstrap Witness
    "BootstrapVerificationResult",
    "BootstrapWitness",
    # Category-Theoretic Protocols
    "Morphism",
    "Functor",
    "get_domain",
    "get_codomain",
    "verify_composition_types",
    # Agent Factory
    "AgentSpec",
    "AgentFactory",
    "FactoryAgent",
    # Grounded Skeleton
    "GroundedSkeleton",
    "AutopoieticAgent",
    # Halo Capability Protocol
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
    # Universal Functor Protocol
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
    # Archetypes
    "Archetype",
    "Kappa",
    "Lambda",
    "Delta",
    "get_archetype",
    "is_archetype_instance",
    # Quick agent creation
    "FunctionAgent",
    "agent",
    "pipeline",
    # =========================================================================
    # LEGACY: Creativity Coach (backwards compat, not core Alethic)
    # =========================================================================
    "CreativityMode",
    "CreativityInput",
    "CreativityResponse",
    "Persona",
    "CreativityCoach",
    "creativity_coach",
    "playful_coach",
    "philosophical_coach",
    "provocative_coach",
]
