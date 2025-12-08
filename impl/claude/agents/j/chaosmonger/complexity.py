"""
Complexity analysis for Python AST.

Provides:
- Cyclomatic complexity calculation
- Branching factor estimation
- Nesting depth analysis
- Runtime complexity estimation
"""

from __future__ import annotations

import ast


def calculate_cyclomatic_complexity(tree: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of the code.

    CC = 1 + number of decision points (if, for, while, try, with, etc.)
    """
    complexity = 1  # Base complexity

    for node in ast.walk(tree):
        # Each decision point adds 1
        if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor)):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(node, ast.comprehension):
            complexity += 1  # List/dict/set comprehensions
        elif isinstance(node, ast.BoolOp):
            # 'and' and 'or' add branches
            complexity += len(node.values) - 1
        elif isinstance(node, ast.IfExp):
            complexity += 1  # Ternary operator

    return complexity


def estimate_branching_factor(tree: ast.AST) -> int:
    """
    Estimate branching factor - expected width of computation tree.

    High branching = wide trees = resource exhaustion risk.
    """
    max_branches = 1

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Count elif/else branches
            branches = 1  # if branch
            if node.orelse:
                branches += 1  # else/elif
            max_branches = max(max_branches, branches)

        elif isinstance(node, ast.Match):
            # Match statement branches
            branches = len(node.cases) if hasattr(node, "cases") else 1
            max_branches = max(max_branches, branches)

        elif isinstance(node, ast.FunctionDef):
            # Count return statements as potential branches
            return_count = sum(
                1 for n in ast.walk(node) if isinstance(n, ast.Return)
            )
            if return_count > 1:
                max_branches = max(max_branches, return_count)

    return max_branches


def calculate_max_nesting(tree: ast.AST) -> int:
    """Calculate maximum nesting depth of control structures."""
    max_depth = 0

    def _walk_with_depth(node: ast.AST, depth: int) -> None:
        nonlocal max_depth

        # Track depth for control structures
        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.Try,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            depth += 1
            max_depth = max(max_depth, depth)

        for child in ast.iter_child_nodes(node):
            _walk_with_depth(child, depth)

    _walk_with_depth(tree, 0)
    return max_depth


def estimate_runtime(tree: ast.AST) -> str:
    """
    Heuristic estimation of runtime complexity.

    Very rough estimate based on nesting of loops.
    """
    max_loop_depth = 0

    def _walk_loops(node: ast.AST, current_depth: int) -> None:
        nonlocal max_loop_depth

        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            current_depth += 1
            max_loop_depth = max(max_loop_depth, current_depth)

        for child in ast.iter_child_nodes(node):
            _walk_loops(child, current_depth)

    _walk_loops(tree, 0)

    if max_loop_depth == 0:
        return "O(1)"
    elif max_loop_depth == 1:
        return "O(n)"
    elif max_loop_depth == 2:
        return "O(n^2)"
    elif max_loop_depth == 3:
        return "O(n^3)"
    else:
        return "unbounded"


def count_functions(tree: ast.AST) -> int:
    """Count function definitions in the AST."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += 1
    return count
