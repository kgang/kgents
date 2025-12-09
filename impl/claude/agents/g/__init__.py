"""
G-gents: The Grammarian

Domain Specific Language synthesis and constraint crystallization.

Key exports:
- Tongue: The reified domain language artifact
- GrammarLevel: SCHEMA, COMMAND, RECURSIVE
- GrammarFormat: BNF, EBNF, LARK, PYDANTIC
- Grammarian: The G-gent synthesis agent
"""

from agents.g.types import (
    Tongue,
    GrammarLevel,
    GrammarFormat,
    ParserConfig,
    InterpreterConfig,
    ConstraintProof,
    Example,
    CounterExample,
    DomainAnalysis,
)

from agents.g.grammarian import (
    Grammarian,
    reify,
    reify_schema,
    reify_command,
    reify_recursive,
)

from agents.g.tongue import (
    create_schema_tongue,
    create_command_tongue,
    create_recursive_tongue,
)

from agents.g.catalog_integration import (
    register_tongue,
    find_tongue,
    check_compatibility,
    find_composable,
    update_tongue_metrics,
)

__all__ = [
    # Core types
    "Tongue",
    "GrammarLevel",
    "GrammarFormat",
    "ParserConfig",
    "InterpreterConfig",
    "ConstraintProof",
    "Example",
    "CounterExample",
    "DomainAnalysis",
    # Agent
    "Grammarian",
    # Convenience functions
    "reify",
    "reify_schema",
    "reify_command",
    "reify_recursive",
    # Template functions
    "create_schema_tongue",
    "create_command_tongue",
    "create_recursive_tongue",
    # L-gent integration
    "register_tongue",
    "find_tongue",
    "check_compatibility",
    "find_composable",
    "update_tongue_metrics",
]
