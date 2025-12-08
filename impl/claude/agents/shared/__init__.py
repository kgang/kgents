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

__all__ = [
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
