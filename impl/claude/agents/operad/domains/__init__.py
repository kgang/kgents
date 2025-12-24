"""
Domain-Specific Operads.

Each domain operad extends AGENT_OPERAD with specialized operations:
- PARSE_OPERAD: P-gent confidence, repair
- REALITY_OPERAD: J-gent classification, collapse
- ANALYSIS_OPERAD: Four modes of rigorous inquiry (categorical, epistemic, dialectical, generative)

Archived (2024-12-24): SOUL_OPERAD, MEMORY_OPERAD, EVOLUTION_OPERAD, NARRATIVE_OPERAD (no callers)
"""

from .analysis import (
    ANALYSIS_OPERAD,
    BootstrapAnalysis,
    CategoricalReport,
    ContradictionType,
    DialecticalReport,
    EpistemicReport,
    EvidenceTier,
    FixedPointAnalysis,
    FullAnalysisReport,
    GenerativeReport,
    GroundingChain,
    OperadGrammar,
    RegenerationTest,
    Tension,
    ToulminStructure,
    create_analysis_operad,
    self_analyze,
)
from .analysis_dp import (
    AnalysisAction,
    AnalysisState,
    analyze_as_dp,
    analyze_with_witness,
    create_analysis_formulation,
    self_analyze_with_dp,
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

__all__ = [
    # Analysis Operad (four modes of inquiry)
    "ANALYSIS_OPERAD",
    "create_analysis_operad",
    "self_analyze",
    # Analysis report types
    "CategoricalReport",
    "EpistemicReport",
    "DialecticalReport",
    "GenerativeReport",
    "FullAnalysisReport",
    # Analysis supporting types
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
]
