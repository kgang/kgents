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

from agents.g.forge_integration import (
    InterfaceTongue,
    TongueEmbedding,
    ArtifactInterface,
    create_artifact_interface,
    embed_tongue_in_contract,
    create_invocation_handler,
    bind_handlers,
    forge_with_interface,
)

from agents.g.fuzzing_integration import (
    # Types
    FuzzInputType,
    FuzzResult,
    FuzzReport,
    PropertyType,
    PropertyResult,
    PropertyTestReport,
    # Classes
    TongueInputGenerator,
    TongueFuzzer,
    TonguePropertyTester,
    # Convenience functions
    fuzz_tongue,
    property_test_tongue,
    validate_tongue_with_t_gent,
    generate_constraint_proofs,
)

from agents.g.pattern_inference import (
    # Types
    PatternType,
    ObservedPattern,
    PatternCluster,
    GrammarRule,
    GrammarHypothesis,
    ValidationResult,
    InferenceReport,
    # Classes
    PatternAnalyzer,
    GrammarSynthesizer,
    GrammarValidator,
    PatternInferenceEngine,
    # Convenience functions
    infer_grammar_from_observations,
    observe_and_infer,
    extract_patterns,
    hypothesize_grammar,
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
    # F-gent integration
    "InterfaceTongue",
    "TongueEmbedding",
    "ArtifactInterface",
    "create_artifact_interface",
    "embed_tongue_in_contract",
    "create_invocation_handler",
    "bind_handlers",
    "forge_with_interface",
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
