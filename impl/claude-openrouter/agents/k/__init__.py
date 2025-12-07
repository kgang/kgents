"""
K-gent: Kent Simulacra

The singular agent—a simulacra of the creator, Kent.
An interactive persona that embodies preferences, values, and thinking patterns.
"""

from .kgent import (
    Kgent,
    kgent,
    query_persona,
    dialogue,
)

from ..types import (
    KgentInput,
    KgentOutput,
    PersonaQuery,
    PersonaUpdate,
    Dialogue,
    DialogueMode,
    QueryAspect,
    UpdateOperation,
    QueryResponse,
    UpdateConfirmation,
    DialogueResponse,
)

__all__ = [
    # Agent
    'Kgent',
    'kgent',

    # Convenience functions
    'query_persona',
    'dialogue',

    # Input types
    'KgentInput',
    'PersonaQuery',
    'PersonaUpdate',
    'Dialogue',
    'DialogueMode',
    'QueryAspect',
    'UpdateOperation',

    # Output types
    'KgentOutput',
    'QueryResponse',
    'UpdateConfirmation',
    'DialogueResponse',
]

# K-gent genus marker
GENUS = 'k'
