"""
Shared utilities across agent genera.

This module contains code extracted from multiple genera that serves
common purposes. Following the SYNERGY_REFACTOR_PLAN, these utilities
are shared but each genus maintains its distinct identity.
"""

from agents.shared.ast_utils import (
    ASTAnalysisKit,
    ClassInfo,
    FunctionInfo,
    calculate_cyclomatic_complexity,
    calculate_max_nesting,
    estimate_branching_factor,
    estimate_runtime_complexity,
    extract_classes,
    extract_functions,
    extract_imports,
    has_unbounded_recursion,
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
]
