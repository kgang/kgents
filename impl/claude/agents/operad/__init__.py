"""
Operad: Grammar of Agent Composition.

Operads make composition rules explicit and programmable.
Instead of hardcoded `>>` operators, operads define a grammar
that constrains and enables valid compositions.

This module provides:
- AGENT_OPERAD: Universal agent composition grammar
- Domain operads: Soul, Parse, Reality (specialized grammars)
- CLIAlgebra: Functor from Operad to CLI commands
- TestAlgebra: Functor from Operad laws to test cases

The key insight: Operad + Primitives → ∞ valid compositions

See: plans/ideas/impl/meta-construction.md
"""

from .algebra import (
    CLIAlgebra,
    CLICommand,
    CLIHandler,
    TestAlgebra,
)
from .core import (
    # Universal operad
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    # Registry
    OperadRegistry,
    # Core types
    Operation,
    create_agent_operad,
)

# Domain operads
from .domains import (
    PARSE_OPERAD,
    REALITY_OPERAD,
    SOUL_OPERAD,
    ConfidentParse,
    ParseResult,
    RealityClassification,
    RealityType,
    create_parse_operad,
    create_reality_operad,
    create_soul_operad,
)

__all__ = [
    # Core types
    "Operation",
    "Law",
    "Operad",
    "LawStatus",
    "LawVerification",
    # Universal operad
    "AGENT_OPERAD",
    "create_agent_operad",
    # Domain operads
    "SOUL_OPERAD",
    "PARSE_OPERAD",
    "REALITY_OPERAD",
    "create_soul_operad",
    "create_parse_operad",
    "create_reality_operad",
    "ParseResult",
    "ConfidentParse",
    "RealityType",
    "RealityClassification",
    # Registry
    "OperadRegistry",
    # CLI Algebra
    "CLIAlgebra",
    "CLICommand",
    "CLIHandler",
    "TestAlgebra",
]
