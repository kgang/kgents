"""
G-gents: The Grammarian

Domain Specific Language synthesis and constraint crystallization.

Key exports:
- Tongue: The reified domain language artifact
- GrammarLevel: SCHEMA, COMMAND, RECURSIVE
- GrammarFormat: BNF, EBNF, LARK, PYDANTIC
- Grammarian: The G-gent synthesis agent
"""

from agents.g.catalog_integration import (
    check_compatibility,
    find_composable,
    find_tongue,
    register_tongue,
    update_tongue_metrics,
)

# forge_integration removed 2025-12-25 (Forge API deprecated)
from agents.g.fuzzing_integration import (
    # Types
    FuzzInputType,
    FuzzReport,
    FuzzResult,
    PropertyResult,
    PropertyTestReport,
    PropertyType,
    TongueFuzzer,
    # Classes
    TongueInputGenerator,
    TonguePropertyTester,
    # Convenience functions
    fuzz_tongue,
    generate_constraint_proofs,
    property_test_tongue,
    validate_tongue_with_t_gent,
)
from agents.g.grammarian import (
    Grammarian,
    reify,
    reify_command,
    reify_recursive,
    reify_schema,
)
from agents.g.pattern_inference import (
    GrammarHypothesis,
    GrammarRule,
    GrammarSynthesizer,
    GrammarValidator,
    InferenceReport,
    ObservedPattern,
    # Classes
    PatternAnalyzer,
    PatternCluster,
    PatternInferenceEngine,
    # Types
    PatternType,
    ValidationResult,
    extract_patterns,
    hypothesize_grammar,
    # Convenience functions
    infer_grammar_from_observations,
    observe_and_infer,
)
from agents.g.tongue import (
    create_command_tongue,
    create_recursive_tongue,
    create_schema_tongue,
)
from agents.g.types import (
    ConstraintProof,
    CounterExample,
    DomainAnalysis,
    Example,
    GrammarFormat,
    GrammarLevel,
    InterpreterConfig,
    ParserConfig,
    Tongue,
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
    # F-gent integration removed 2025-12-25 (Forge API deprecated)
    # T-gent integration (Phase 6)
    "FuzzInputType",
    "FuzzResult",
    "FuzzReport",
    "PropertyType",
    "PropertyResult",
    "PropertyTestReport",
    "TongueInputGenerator",
    "TongueFuzzer",
    "TonguePropertyTester",
    "fuzz_tongue",
    "property_test_tongue",
    "validate_tongue_with_t_gent",
    "generate_constraint_proofs",
    # W-gent integration (Phase 7)
    "PatternType",
    "ObservedPattern",
    "PatternCluster",
    "GrammarRule",
    "GrammarHypothesis",
    "ValidationResult",
    "InferenceReport",
    "PatternAnalyzer",
    "GrammarSynthesizer",
    "GrammarValidator",
    "PatternInferenceEngine",
    "infer_grammar_from_observations",
    "observe_and_infer",
    "extract_patterns",
    "hypothesize_grammar",
]
