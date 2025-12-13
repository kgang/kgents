"""
Sheaf: Emergence Infrastructure.

Sheaves capture the mathematical structure of emergence:
- Local sections: Context-specific behaviors
- Gluing: Combine compatible behaviors
- Restriction: Extract local from global

This module provides:
- AgentSheaf: Generic sheaf over contexts
- SOUL_SHEAF: Sheaf over eigenvector contexts
- Emergence: Glued Kent Soul from local souls

The key insight: Global behavior EMERGES from gluing
compatible local behaviors. The emergent soul has
capabilities no single local soul possesses.

See: plans/ideas/impl/meta-construction.md
"""

from .emergence import (
    KENT_SOUL,
    create_aesthetic_soul,
    create_categorical_soul,
    create_emergent_soul,
    create_generativity_soul,
    create_gratitude_soul,
    create_heterarchy_soul,
    create_joy_soul,
    query_soul,
)
from .protocol import (
    AESTHETIC,
    CATEGORICAL,
    GENERATIVITY,
    GRATITUDE,
    HETERARCHY,
    JOY,
    SOUL_SHEAF,
    AgentSheaf,
    Context,
    GluingError,
    RestrictionError,
    create_soul_sheaf,
    eigenvector_overlap,
)

__all__ = [
    # Core types
    "Context",
    "GluingError",
    "RestrictionError",
    # Sheaf
    "AgentSheaf",
    # Soul Sheaf
    "SOUL_SHEAF",
    "create_soul_sheaf",
    # Contexts
    "AESTHETIC",
    "CATEGORICAL",
    "GRATITUDE",
    "HETERARCHY",
    "GENERATIVITY",
    "JOY",
    "eigenvector_overlap",
    # Local souls
    "create_aesthetic_soul",
    "create_categorical_soul",
    "create_gratitude_soul",
    "create_heterarchy_soul",
    "create_generativity_soul",
    "create_joy_soul",
    # Emergent soul
    "create_emergent_soul",
    "KENT_SOUL",
    "query_soul",
]
