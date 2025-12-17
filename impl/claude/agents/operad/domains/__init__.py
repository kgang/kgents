"""
Domain-Specific Operads.

Each domain operad extends AGENT_OPERAD with specialized operations:
- SOUL_OPERAD: K-gent introspection, shadow, dialectic
- PARSE_OPERAD: P-gent confidence, repair
- REALITY_OPERAD: J-gent classification, collapse
- MEMORY_OPERAD: D-gent persistence, recall, forget
- EVOLUTION_OPERAD: Generic evolution (mutation, selection, convergence)
- NARRATIVE_OPERAD: N-gent chronicle, branch, merge
"""

from .evolution import (
    EVOLUTION_OPERAD,
    create_evolution_operad,
)
from .memory import (
    MEMORY_OPERAD,
    create_memory_operad,
)
from .narrative import (
    NARRATIVE_OPERAD,
    create_narrative_operad,
)
from .parse import (
    PARSE_OPERAD,
    ConfidentParse,
    ParseResult,
    create_parse_operad,
)
from .reality import (
    REALITY_OPERAD,
    RealityClassification,
    RealityType,
    create_reality_operad,
)
from .soul import (
    SOUL_OPERAD,
    create_soul_operad,
)

__all__ = [
    # Soul (K-gent)
    "SOUL_OPERAD",
    "create_soul_operad",
    # Parse (P-gent)
    "PARSE_OPERAD",
    "ParseResult",
    "ConfidentParse",
    "create_parse_operad",
    # Reality (J-gent)
    "REALITY_OPERAD",
    "RealityType",
    "RealityClassification",
    "create_reality_operad",
    # Memory (D-gent)
    "MEMORY_OPERAD",
    "create_memory_operad",
    # Evolution (generic, E-gent archived)
    "EVOLUTION_OPERAD",
    "create_evolution_operad",
    # Narrative (N-gent)
    "NARRATIVE_OPERAD",
    "create_narrative_operad",
]
