"""
A-gents: Abstract Architectures + Art/Creativity

A-gents provide:
- The agent skeleton (what every agent MUST be)
- Creativity-focused agents for idea expansion
- Bootstrap verification (BootstrapWitness)
- Category-theoretic protocols (Morphism, Functor)
- Agent factory (AgentFactory)
- Self-describing agents (GroundedSkeleton)

The key insight of A-gents: Agent[A, B] from bootstrap IS the skeleton.
AbstractAgent is just an alias for semantic clarity.

For richer metadata, use AgentMeta (optional).
"""

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
]
