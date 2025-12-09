"""
Shared utilities across agent genera.

This module contains code extracted from multiple genera that serves
common purposes. Following the SYNERGY_REFACTOR_PLAN, these utilities
are shared but each genus maintains its distinct identity.
"""

from agents.shared.ast_utils import (
    ASTAnalysisKit,
    extract_imports,
    calculate_cyclomatic_complexity,
    calculate_max_nesting,
    estimate_branching_factor,
    estimate_runtime_complexity,
    has_unbounded_recursion,
    extract_functions,
    extract_classes,
    FunctionInfo,
    ClassInfo,
)
from agents.shared.fixtures import (
    make_sample_intent,
    make_sample_contract,
    make_sample_source_code,
    make_simple_agent_code,
    make_sample_catalog_entry,
)

__all__ = [
    # AST utilities
    "ASTAnalysisKit",
    "extract_imports",
    "calculate_cyclomatic_complexity",
    "calculate_max_nesting",
    "estimate_branching_factor",
    "estimate_runtime_complexity",
    "has_unbounded_recursion",
    "extract_functions",
    "extract_classes",
    "FunctionInfo",
    "ClassInfo",
    # Test fixtures
    "make_sample_intent",
    "make_sample_contract",
    "make_sample_source_code",
    "make_simple_agent_code",
    "make_sample_catalog_entry",
]
