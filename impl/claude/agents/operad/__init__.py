"""
Operad: Grammar of Agent Composition.

Operads make composition rules explicit and programmable.
Instead of hardcoded `>>` operators, operads define a grammar
that constrains and enables valid compositions.

This module provides:
- AGENT_OPERAD: Universal agent composition grammar
- Domain operads: Parse, Reality (specialized grammars)
- CLIAlgebra: Functor from Operad to CLI commands
- TestAlgebra: Functor from Operad laws to test cases

The key insight: Operad + Primitives → ∞ valid compositions

Archived (2024-12-24): Soul, Memory, Evolution, Narrative operads (no callers)

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
    # Analysis Operad
    ANALYSIS_OPERAD,
    # Probe Operad
    ASSOCIATIVITY_LAW,
    BRANCH_OP,
    FIX_OP,
    IDENTITY_LAW,
    PAR_OP,
    # Parse Operad
    PARSE_OPERAD,
    PROBE_OPERAD,
    # Reality Operad
    REALITY_OPERAD,
    SEQ_OP,
    TRACE_PRESERVATION_LAW,
    WITNESS_OP,
    # Analysis DP integration
    AnalysisAction,
    AnalysisState,
    BootstrapAnalysis,
    BranchProbe,
    CategoricalReport,
    ConfidentParse,
    ContradictionType,
    DialecticalReport,
    EpistemicReport,
    EvidenceTier,
    FixedPointAnalysis,
    FixedPointProbe,
    FullAnalysisReport,
    GenerativeReport,
    GroundingChain,
    NullProbe,
    OperadGrammar,
    ParallelProbe,
    ParseResult,
    ProbeProtocol,
    RealityClassification,
    RealityType,
    RegenerationTest,
    SequentialProbe,
    Tension,
    ToulminStructure,
    WitnessedProbe,
    analyze_as_dp,
    analyze_with_witness,
    create_analysis_formulation,
    create_analysis_operad,
    create_parse_operad,
    create_probe_operad,
    create_reality_operad,
    self_analyze,
    self_analyze_with_dp,
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
    # Analysis Operad (four modes of inquiry)
    "ANALYSIS_OPERAD",
    "create_analysis_operad",
    "self_analyze",
    "CategoricalReport",
    "EpistemicReport",
    "DialecticalReport",
    "GenerativeReport",
    "FullAnalysisReport",
    "ContradictionType",
    "EvidenceTier",
    "FixedPointAnalysis",
    "ToulminStructure",
    "GroundingChain",
    "BootstrapAnalysis",
    "Tension",
    "OperadGrammar",
    "RegenerationTest",
    # Analysis DP integration
    "AnalysisState",
    "AnalysisAction",
    "create_analysis_formulation",
    "analyze_as_dp",
    "analyze_with_witness",
    "self_analyze_with_dp",
    # Parse Operad
    "PARSE_OPERAD",
    "create_parse_operad",
    "ParseResult",
    "ConfidentParse",
    # Probe Operad (verification composition)
    "PROBE_OPERAD",
    "create_probe_operad",
    "ProbeProtocol",
    "SequentialProbe",
    "ParallelProbe",
    "BranchProbe",
    "FixedPointProbe",
    "WitnessedProbe",
    "NullProbe",
    "SEQ_OP",
    "PAR_OP",
    "BRANCH_OP",
    "FIX_OP",
    "WITNESS_OP",
    "ASSOCIATIVITY_LAW",
    "IDENTITY_LAW",
    "TRACE_PRESERVATION_LAW",
    # Reality Operad
    "REALITY_OPERAD",
    "create_reality_operad",
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
