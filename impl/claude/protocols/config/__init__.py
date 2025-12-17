"""
Configuration module for kgents SaaS infrastructure.

Provides centralized configuration for:
- NATS streaming
- OpenMeter usage billing
- Other SaaS service integrations
- DNA: Agent configuration as genetic code (from bootstrap)
"""

from .clients import (
    SaaSClients,
    get_saas_clients,
    init_saas_clients,
    reset_saas_clients,
    shutdown_saas_clients,
)
from .dna import (
    BOUNDED_DEPTH,
    DNA,
    EPISTEMIC_HUMILITY,
    POPPERIAN_PRINCIPLE,
    POSITIVE_EXPLORATION,
    BaseDNA,
    ComposedDNA,
    Constraint,
    ContextModifier,
    DNAModifier,
    DNAValidationError,
    HypothesisDNA,
    JGentDNA,
    LLMAgentDNA,
    RiskAwareAgentDNA,
    StatefulAgentDNA,
    TraitNotFoundError,
    UrgencyModifier,
)
from .saas import (
    SaaSConfig,
    get_cached_saas_config,
    get_saas_config,
    reset_cached_config,
)

__all__ = [
    # Config
    "SaaSConfig",
    "get_saas_config",
    "get_cached_saas_config",
    "reset_cached_config",
    # Clients
    "SaaSClients",
    "get_saas_clients",
    "init_saas_clients",
    "shutdown_saas_clients",
    "reset_saas_clients",
    # DNA (migrated from bootstrap)
    "DNA",
    "DNAValidationError",
    "TraitNotFoundError",
    "Constraint",
    "DNAModifier",
    "ComposedDNA",
    "BaseDNA",
    "LLMAgentDNA",
    "StatefulAgentDNA",
    "RiskAwareAgentDNA",
    "HypothesisDNA",
    "JGentDNA",
    "UrgencyModifier",
    "ContextModifier",
    "EPISTEMIC_HUMILITY",
    "POSITIVE_EXPLORATION",
    "BOUNDED_DEPTH",
    "POPPERIAN_PRINCIPLE",
]
