"""
Shared AST utilities for all agent genera.

Extracted from J-gents Chaosmonger and various AST analyzers as per
SYNERGY_REFACTOR_PLAN Phase 4A.

Provides common AST operations:
- Import extraction
- Complexity calculation
- Nesting depth analysis
- Branching factor estimation
- Function/class extraction

Enhanced (Phase D - H15) with formal visitor pattern for extensible AST traversal.
"""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


@dataclass(frozen=True)
class FunctionInfo:
    """Information about a function extracted from AST."""

    name: str
    lineno: int
    end_lineno: Optional[int]
    args: tuple[str, ...]
    is_async: bool
    is_private: bool
    has_docstring: bool
    return_annotation: Optional[str] = None


@dataclass(frozen=True)
class ClassInfo:
    """Information about a class extracted from AST."""

    name: str
    lineno: int
    end_lineno: Optional[int]
    methods: tuple[FunctionInfo, ...]
    bases: tuple[str, ...]
    has_docstring: bool


# --- Import Analysis (from J-gents Chaosmonger) ---


def extract_imports(tree: ast.AST) -> list[str]:
    """
    Extract all imported module names from AST.

    Returns the base module name (e.g., "os" from "os.path").

    Args:
        tree: Parsed AST

    Returns:
        List of unique base module names
    """
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get the base module (e.g., "os" from "os.path")
                base = alias.name.split(".")[0]
                imports.append(base)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base = node.module.split(".")[0]
                imports.append(base)

    return imports


def extract_imports_detailed(tree: ast.AST) -> list[str]:
    """
    Extract full import paths from AST.

    Returns the full import path (e.g., "os.path" from "from os import path").

    Args:
        tree: Parsed AST

    Returns:
        List of full import paths
    """
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

    return imports


# --- Complexity Analysis (from J-gents Chaosmonger) ---


def calculate_cyclomatic_complexity(tree: ast.AST) -> int:
    """
    Calculate cyclomatic complexity of the code.

    CC = 1 + number of decision points (if, for, while, try, with, etc.)

    Args:
        tree: Parsed AST

    Returns:
        Cyclomatic complexity score
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


def calculate_max_nesting(tree: ast.AST) -> int:
    """
    Calculate maximum nesting depth of control structures.

    Args:
        tree: Parsed AST

    Returns:
        Maximum nesting depth
    """
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


def estimate_branching_factor(tree: ast.AST) -> int:
    """
    Estimate branching factor - expected width of computation tree.

    High branching = wide trees = resource exhaustion risk.

    Args:
        tree: Parsed AST

    Returns:
        Maximum branching factor
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
            return_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
            if return_count > 1:
                max_branches = max(max_branches, return_count)

    return max_branches


def estimate_runtime_complexity(tree: ast.AST) -> str:
    """
    Heuristic estimation of runtime complexity.

    Very rough estimate based on nesting of loops.

    Args:
        tree: Parsed AST

    Returns:
        Complexity estimate: "O(1)", "O(n)", "O(n^2)", "O(n^3)", or "unbounded"
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


# --- Recursion Detection (from J-gents Chaosmonger) ---


def has_unbounded_recursion(tree: ast.AST) -> bool:
    """
    Detect patterns that may never terminate.

    Checks for:
    1. while True without break
    2. Recursive functions without apparent base case

    Args:
        tree: Parsed AST

    Returns:
        True if unbounded recursion detected
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
    for stmt in body[:3]:  # Look at first 3 statements
        if isinstance(stmt, ast.Return):
            return True  # Early return = base case
        if isinstance(stmt, ast.If):
            # Check if the if block has a return
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Return):
                    return True

    return False


# --- Structure Extraction ---


def extract_functions(tree: ast.AST) -> list[FunctionInfo]:
    """
    Extract function information from AST.

    Args:
        tree: Parsed AST

    Returns:
        List of FunctionInfo for top-level functions
    """
    functions: list[FunctionInfo] = []

    # Get all class bodies to exclude methods
    class_bodies: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                class_bodies.add(id(item))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip if this is a method (in a class body)
            if id(node) in class_bodies:
                continue

            # Check for docstring
            has_docstring = bool(
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )

            # Get return annotation
            return_annotation = None
            if node.returns:
                try:
                    return_annotation = ast.unparse(node.returns)
                except Exception:
                    pass

            functions.append(
                FunctionInfo(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", None),
                    args=tuple(a.arg for a in node.args.args),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    is_private=node.name.startswith("_"),
                    has_docstring=has_docstring,
                    return_annotation=return_annotation,
                )
            )

    return functions


def extract_classes(tree: ast.AST) -> list[ClassInfo]:
    """
    Extract class information from AST.

    Args:
        tree: Parsed AST

    Returns:
        List of ClassInfo
    """
    classes: list[ClassInfo] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods: list[FunctionInfo] = []

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_has_docstring = bool(
                        item.body
                        and isinstance(item.body[0], ast.Expr)
                        and isinstance(item.body[0].value, ast.Constant)
                        and isinstance(item.body[0].value.value, str)
                    )

                    return_annotation = None
                    if item.returns:
                        try:
                            return_annotation = ast.unparse(item.returns)
                        except Exception:
                            pass

                    methods.append(
                        FunctionInfo(
                            name=item.name,
                            lineno=item.lineno,
                            end_lineno=getattr(item, "end_lineno", None),
                            args=tuple(a.arg for a in item.args.args),
                            is_async=isinstance(item, ast.AsyncFunctionDef),
                            is_private=item.name.startswith("_"),
                            has_docstring=method_has_docstring,
                            return_annotation=return_annotation,
                        )
                    )

            # Check for class docstring
            class_has_docstring = bool(
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )

            # Get bases
            bases = []
            for base in node.bases:
                try:
                    bases.append(ast.unparse(base))
                except Exception:
                    pass

            classes.append(
                ClassInfo(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=getattr(node, "end_lineno", None),
                    methods=tuple(methods),
                    bases=tuple(bases),
                    has_docstring=class_has_docstring,
                )
            )

    return classes


def count_functions(tree: ast.AST) -> int:
    """Count function definitions in the AST."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            count += 1
    return count


# --- Convenience Class ---


class ASTAnalysisKit:
    """
    Common AST operations for all genera.

    Provides a unified interface to all shared AST utilities.

    Usage:
        tree = ast.parse(source_code)
        kit = ASTAnalysisKit(tree)

        print(f"Complexity: {kit.cyclomatic_complexity}")
        print(f"Imports: {kit.imports}")
        print(f"Functions: {kit.functions}")
    """

    def __init__(self, tree: ast.AST):
        """
        Initialize with a parsed AST.

        Args:
            tree: Parsed AST from ast.parse()
        """
        self._tree = tree
        # Lazy computed properties
        self._imports: Optional[list[str]] = None
        self._complexity: Optional[int] = None
        self._nesting: Optional[int] = None
        self._branching: Optional[int] = None
        self._runtime: Optional[str] = None
        self._unbounded: Optional[bool] = None
        self._functions: Optional[list[FunctionInfo]] = None
        self._classes: Optional[list[ClassInfo]] = None

    @classmethod
    def from_source(cls, source: str) -> "ASTAnalysisKit":
        """
        Create from source code string.

        Args:
            source: Python source code

        Returns:
            ASTAnalysisKit instance

        Raises:
            SyntaxError: If source cannot be parsed
        """
        return cls(ast.parse(source))

    @property
    def imports(self) -> list[str]:
        """Get base module imports."""
        if self._imports is None:
            self._imports = extract_imports(self._tree)
        return self._imports

    @property
    def imports_detailed(self) -> list[str]:
        """Get full import paths."""
        return extract_imports_detailed(self._tree)

    @property
    def cyclomatic_complexity(self) -> int:
        """Get cyclomatic complexity."""
        if self._complexity is None:
            self._complexity = calculate_cyclomatic_complexity(self._tree)
        return self._complexity

    @property
    def max_nesting_depth(self) -> int:
        """Get maximum nesting depth."""
        if self._nesting is None:
            self._nesting = calculate_max_nesting(self._tree)
        return self._nesting

    @property
    def branching_factor(self) -> int:
        """Get branching factor."""
        if self._branching is None:
            self._branching = estimate_branching_factor(self._tree)
        return self._branching

    @property
    def runtime_complexity(self) -> str:
        """Get estimated runtime complexity."""
        if self._runtime is None:
            self._runtime = estimate_runtime_complexity(self._tree)
        return self._runtime

    @property
    def has_unbounded_recursion(self) -> bool:
        """Check for unbounded recursion."""
        if self._unbounded is None:
            self._unbounded = has_unbounded_recursion(self._tree)
        return self._unbounded

    @property
    def functions(self) -> list[FunctionInfo]:
        """Get function information."""
        if self._functions is None:
            self._functions = extract_functions(self._tree)
        return self._functions

    @property
    def classes(self) -> list[ClassInfo]:
        """Get class information."""
        if self._classes is None:
            self._classes = extract_classes(self._tree)
        return self._classes

    @property
    def function_count(self) -> int:
        """Get total function count (including methods)."""
        return count_functions(self._tree)


# ============================================================================
# Formal Visitor Pattern (Phase D - H15)
# ============================================================================
# Provides extensible AST traversal for custom analysis without modifying
# existing utility functions.


T = TypeVar("T")


class ASTVisitor(ABC, Generic[T]):
    """
    Abstract base class for AST visitors.

    Implements the Visitor pattern for extensible AST traversal.
    Subclasses override visit_* methods for specific node types.

    Generic type T represents the accumulated result type.

    Usage:
        class ImportCollector(ASTVisitor[list[str]]):
            def __init__(self):
                self.imports = []

            def visit_Import(self, node: ast.Import) -> None:
                for alias in node.names:
                    self.imports.append(alias.name)

            def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
                if node.module:
                    self.imports.append(node.module)

            def result(self) -> list[str]:
                return self.imports

        tree = ast.parse(source)
        visitor = ImportCollector()
        visitor.visit(tree)
        print(visitor.result())
    """

    def visit(self, node: ast.AST) -> None:
        """
        Visit a node and dispatch to specialized visit_* method.

        Args:
            node: AST node to visit
        """
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node: ast.AST) -> None:
        """
        Default visitor for unhandled node types.

        Recursively visits all child nodes.

        Args:
            node: AST node to visit
        """
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    @abstractmethod
    def result(self) -> T:
        """
        Return the accumulated result of the visitor.

        Returns:
            Result of type T
        """
        pass


class ComplexityVisitor(ASTVisitor[int]):
    """
    Visitor that calculates cyclomatic complexity.

    Demonstrates the visitor pattern by reimplementing
    calculate_cyclomatic_complexity as a visitor.

    Complexity = 1 + decision points (if, for, while, etc.)
    """

    def __init__(self) -> None:
        """Initialize with base complexity of 1."""
        self._complexity = 1

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Visit async for loop - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit exception handler - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statement - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Visit async with statement - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        """Visit comprehension - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operation - adds branches - 1 to complexity."""
        self._complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        """Visit ternary expression - adds 1 to complexity."""
        self._complexity += 1
        self.generic_visit(node)

    def result(self) -> int:
        """Return calculated cyclomatic complexity."""
        return self._complexity


class ImportVisitor(ASTVisitor[list[str]]):
    """
    Visitor that collects all imports.

    Demonstrates visitor pattern for import extraction.
    """

    def __init__(self, detailed: bool = False):
        """
        Initialize import visitor.

        Args:
            detailed: If True, collect full paths (os.path), else base names (os)
        """
        self._imports: list[str] = []
        self._detailed = detailed

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            if self._detailed:
                self._imports.append(alias.name)
            else:
                # Get base module name
                self._imports.append(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statement."""
        if node.module:
            if self._detailed:
                # Detailed: include what's imported (os.path.join)
                for alias in node.names:
                    self._imports.append(f"{node.module}.{alias.name}")
            else:
                # Base: just the module (os)
                self._imports.append(node.module.split(".")[0])
        self.generic_visit(node)

    def result(self) -> list[str]:
        """Return collected imports."""
        return self._imports


def visit_ast(tree: ast.AST, visitor: ASTVisitor[T]) -> T:
    """
    Visit an AST with a visitor and return result.

    Convenience function for visitor pattern usage.

    Args:
        tree: AST to visit
        visitor: Visitor instance

    Returns:
        Result from visitor.result()

    Example:
        tree = ast.parse(source)
        complexity = visit_ast(tree, ComplexityVisitor())
        imports = visit_ast(tree, ImportVisitor(detailed=True))
    """
    visitor.visit(tree)
    return visitor.result()
