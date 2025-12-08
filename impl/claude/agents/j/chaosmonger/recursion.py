"""
Unbounded recursion and infinite loop detection.

Detects patterns that may never terminate:
- while True without break
- Recursive functions without base case
"""

from __future__ import annotations

import ast


def has_unbounded_recursion(tree: ast.AST) -> bool:
    """
    Detect patterns that may never terminate.

    Checks for:
    1. while True without break
    2. Recursive functions without apparent base case
    """
    function_names: set[str] = set()
    recursive_functions: set[str] = set()

    # First pass: collect function names
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.add(node.name)

    # Second pass: check for unbounded patterns
    for node in ast.walk(tree):
        # Pattern 1: while True without break
        if isinstance(node, ast.While):
            if _is_always_true(node.test) and not _has_break_in_loop(node):
                return True

        # Pattern 2: Check for recursive calls
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            if _calls_self(node, func_name) and not _has_base_case(node):
                recursive_functions.add(func_name)

    # If any function is recursive without base case, flag it
    return len(recursive_functions) > 0


def _is_always_true(node: ast.expr) -> bool:
    """Check if an expression is always true."""
    if isinstance(node, ast.Constant):
        return bool(node.value)
    if isinstance(node, ast.NameConstant):  # Python 3.7 compatibility
        return bool(node.value)
    return False


def _has_break_in_loop(node: ast.While | ast.For) -> bool:
    """Check if a loop body contains a break statement."""
    for child in ast.walk(node):
        if isinstance(child, ast.Break):
            return True
        # Don't look into nested loops
        if child is not node and isinstance(child, (ast.While, ast.For)):
            continue
    return False


def _calls_self(func: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    """Check if a function calls itself."""
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == name:
                return True
    return False


def _has_base_case(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """
    Heuristic: check if function has an early return or base case pattern.

    Looks for:
    - Return before any recursive call
    - If statement at the start with a return
    """
    body = func.body
    if not body:
        return False

    # Check first few statements for base case pattern
    for i, stmt in enumerate(body[:3]):  # Look at first 3 statements
        if isinstance(stmt, ast.Return):
            return True  # Early return = base case
        if isinstance(stmt, ast.If):
            # Check if the if block has a return
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Return):
                    return True

    return False
