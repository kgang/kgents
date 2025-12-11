"""Tests for shared AST utilities."""

import ast

import pytest
from agents.shared.ast_utils import (
    ASTAnalysisKit,
    calculate_cyclomatic_complexity,
    calculate_max_nesting,
    estimate_branching_factor,
    estimate_runtime_complexity,
    extract_classes,
    extract_functions,
    extract_imports,
    has_unbounded_recursion,
)

# --- Test Fixtures ---


SIMPLE_CODE = '''
import json
from typing import List

def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
'''

COMPLEX_CODE = '''
import os
import sys
from pathlib import Path
from typing import Optional, List

class DataProcessor:
    """Processes data."""

    def __init__(self, path: Path):
        self.path = path

    def process(self, data: List[str]) -> Optional[str]:
        """Process the data."""
        if not data:
            return None

        result = []
        for item in data:
            if item.startswith("_"):
                continue
            for char in item:
                if char.isalpha():
                    result.append(char)
        return "".join(result)

    def _helper(self) -> None:
        pass


def standalone_func(x: int, y: int) -> int:
    return x + y
'''

# Note: The unbounded recursion detection is heuristic.
# It looks for functions that call themselves without a clear base case pattern
# (an if statement with a return in the first 3 statements).
# For this test, we use a function without any early return pattern.
RECURSIVE_CODE = """
def infinite_recurse(n):
    x = n + 1
    y = infinite_recurse(x)
    z = y + 1
    return z
"""

RECURSIVE_WITH_BASE = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

INFINITE_LOOP = """
def run():
    while True:
        pass
"""

LOOP_WITH_BREAK = """
def run():
    while True:
        if should_stop():
            break
"""


# --- Test Import Extraction ---


def test_extract_imports_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    imports = extract_imports(tree)
    assert "json" in imports
    assert "typing" in imports


def test_extract_imports_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    imports = extract_imports(tree)
    assert "os" in imports
    assert "sys" in imports
    assert "pathlib" in imports
    assert "typing" in imports


# --- Test Complexity Calculation ---


def test_cyclomatic_complexity_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    cc = calculate_cyclomatic_complexity(tree)
    assert cc == 1  # No branches


def test_cyclomatic_complexity_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    cc = calculate_cyclomatic_complexity(tree)
    assert cc > 1  # Multiple branches


def test_max_nesting_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    depth = calculate_max_nesting(tree)
    assert depth == 1  # Just the function


def test_max_nesting_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    depth = calculate_max_nesting(tree)
    assert depth >= 3  # Class -> method -> for -> for/if


# --- Test Branching Factor ---


def test_branching_factor_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    bf = estimate_branching_factor(tree)
    assert bf == 1  # No branches


def test_branching_factor_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    bf = estimate_branching_factor(tree)
    assert bf >= 1


# --- Test Runtime Estimation ---


def test_runtime_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    rt = estimate_runtime_complexity(tree)
    assert rt == "O(1)"


def test_runtime_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    rt = estimate_runtime_complexity(tree)
    assert rt in ["O(n)", "O(n^2)"]  # Nested loops


# --- Test Recursion Detection ---


def test_unbounded_recursion_detected() -> None:
    tree = ast.parse(RECURSIVE_CODE)
    assert has_unbounded_recursion(tree) is True


def test_recursion_with_base_case_allowed() -> None:
    tree = ast.parse(RECURSIVE_WITH_BASE)
    assert has_unbounded_recursion(tree) is False


def test_infinite_loop_detected() -> None:
    tree = ast.parse(INFINITE_LOOP)
    assert has_unbounded_recursion(tree) is True


def test_loop_with_break_allowed() -> None:
    tree = ast.parse(LOOP_WITH_BREAK)
    assert has_unbounded_recursion(tree) is False


# --- Test Function Extraction ---


def test_extract_functions_simple() -> None:
    tree = ast.parse(SIMPLE_CODE)
    funcs = extract_functions(tree)
    assert len(funcs) == 1
    assert funcs[0].name == "hello"
    assert funcs[0].has_docstring is True
    assert funcs[0].return_annotation == "str"


def test_extract_functions_complex() -> None:
    tree = ast.parse(COMPLEX_CODE)
    funcs = extract_functions(tree)
    # Only standalone_func, not methods
    assert len(funcs) == 1
    assert funcs[0].name == "standalone_func"


# --- Test Class Extraction ---


def test_extract_classes() -> None:
    tree = ast.parse(COMPLEX_CODE)
    classes = extract_classes(tree)
    assert len(classes) == 1
    cls = classes[0]
    assert cls.name == "DataProcessor"
    assert len(cls.methods) == 3
    method_names = [m.name for m in cls.methods]
    assert "__init__" in method_names
    assert "process" in method_names
    assert "_helper" in method_names


# --- Test ASTAnalysisKit ---


def test_kit_from_source() -> None:
    kit = ASTAnalysisKit.from_source(COMPLEX_CODE)
    assert kit.cyclomatic_complexity > 1
    assert "os" in kit.imports
    assert len(kit.classes) == 1
    assert len(kit.functions) == 1


def test_kit_lazy_evaluation() -> None:
    kit = ASTAnalysisKit.from_source(SIMPLE_CODE)
    # Access properties multiple times
    _ = kit.imports
    _ = kit.imports
    _ = kit.cyclomatic_complexity
    _ = kit.cyclomatic_complexity
    # Should use cached values (no exception)


def test_kit_detailed_imports() -> None:
    kit = ASTAnalysisKit.from_source(COMPLEX_CODE)
    detailed = kit.imports_detailed
    assert any("Path" in imp for imp in detailed)
    assert any("Optional" in imp for imp in detailed)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
