"""
P-gents: Parser Agents

Bridging the Stochastic-Structural Gap between LLM outputs and deterministic parsers.

Core Philosophy: Fuzzy coercion without opinion
- Prevention: Constrain generation to make invalid outputs impossible
- Correction: Repair malformed outputs with high-confidence heuristics
- Novel: First-principles techniques that reframe the problem

Key Exports:
- ParseResult: Transparent parsing result with confidence scoring
- Parser: Parser protocol for composable parsing strategies
- ParserConfig: Configuration for parser behavior

Strategies:
- Prevention: CFGConstrainedParser, FIMSandwichParser, TypeGuidedParser
- Correction: StackBalancingParser, StructuralDecouplingParser, IncrementalParser
- Novel: AnchorBasedParser, DiffBasedParser, ProbabilisticASTParser, EvolvingParser
- Composition: FallbackParser, FusionParser, SwitchParser
"""

from agents.p.composition import FallbackParser, FusionParser, SwitchParser
from agents.p.core import Parser, ParserConfig, ParseResult
from agents.p.strategies.anchor import AnchorBasedParser
from agents.p.strategies.diff_based import (
    DiffBasedParser,
    create_code_diff_parser,
    create_wgent_diff_parser,
)
from agents.p.strategies.evolving import (
    DriftReport,
    EvolvingParser,
    FormatStats,
    create_multi_format_parser,
)
from agents.p.strategies.probabilistic_ast import (
    ProbabilisticASTNode,
    ProbabilisticASTParser,
    get_low_confidence_paths,
    query_confident_fields,
)
from agents.p.strategies.reflection import (
    ReflectionContext,
    ReflectionParser,
    create_reflection_parser_with_llm,
)
from agents.p.strategies.stack_balancing import (
    StackBalancingParser,
    html_stream_parser,
    json_stream_parser,
)

__all__ = [
    # Core types
    "ParseResult",
    "Parser",
    "ParserConfig",
    "ReflectionContext",
    # Phase 1 & 2 Strategies
    "AnchorBasedParser",
    "StackBalancingParser",
    "ReflectionParser",
    "html_stream_parser",
    "json_stream_parser",
    "create_reflection_parser_with_llm",
    # Phase 3 Novel Strategies
    "DiffBasedParser",
    "create_wgent_diff_parser",
    "create_code_diff_parser",
    "ProbabilisticASTParser",
    "ProbabilisticASTNode",
    "query_confident_fields",
    "get_low_confidence_paths",
    "EvolvingParser",
    "FormatStats",
    "DriftReport",
    "create_multi_format_parser",
    # Composition
    "FallbackParser",
    "FusionParser",
    "SwitchParser",
]
