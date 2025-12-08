"""
K-gent: Kent Simulacra

The personalizer - Ground projected through persona_schema.

K-gent provides:
- Queryable preferences for other agents
- Dialogue modes (reflect, advise, challenge, explore)
- Evolution through interaction

K-gent is NOT Kent. It is a mirror for self-dialogue and a personalization
layer for the entire kgents ecosystem.
"""

from .persona import (
    PersonaSeed,
    PersonaState,
    PersonaQuery,
    PersonaResponse,
    DialogueMode,
    DialogueInput,
    DialogueOutput,
    KgentAgent,
    PersonaQueryAgent,
    kgent,
    query_persona,
)

from .evolution import (
    EvolutionInput,
    EvolutionOutput,
    ConfidenceLevel,
    ChangeSource,
    EvolutionAgent,
    evolve_persona,
    # Bootstrap
    BootstrapMode,
    BootstrapConfig,
    bootstrap_persona,
    bootstrap_clean_slate,
    bootstrap_hybrid,
    # Conflict detection
    ConflictData,
    ConflictDetector,
)

__all__ = [
    # Persona types
    "PersonaSeed",
    "PersonaState",
    "PersonaQuery",
    "PersonaResponse",
    "DialogueMode",
    "DialogueInput",
    "DialogueOutput",
    # Agents
    "KgentAgent",
    "PersonaQueryAgent",
    "EvolutionAgent",
    # Convenience functions
    "kgent",
    "query_persona",
    "evolve_persona",
    # Evolution types
    "EvolutionInput",
    "EvolutionOutput",
    "ConfidenceLevel",
    "ChangeSource",
    # Bootstrap
    "BootstrapMode",
    "BootstrapConfig",
    "bootstrap_persona",
    "bootstrap_clean_slate",
    "bootstrap_hybrid",
    # Conflict detection
    "ConflictData",
    "ConflictDetector",
]
