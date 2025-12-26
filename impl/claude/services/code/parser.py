"""
Python AST Parser for FunctionCrystal extraction.

Parses Python source files and extracts:
- Function definitions with signatures
- Docstrings
- Parameter info with types
- Import statements
- Call graph (which functions call which)
- Line ranges
- Body hashes for change detection

This module provides the parsing layer for the Unified Crystal Taxonomy.
It converts Python source code into FunctionCrystal objects that can be
stored, analyzed, and proven.

Philosophy:
- Every function is a crystal (self-contained unit of meaning)
- Parsing extracts structure, not semantics
- Body hash enables change detection
- Call graph enables dependency analysis

Usage:
    from services.code.parser import parse_file, FunctionInfo

    # Parse a file
    functions = parse_file("/path/to/file.py")

    # Convert to crystals
    from agents.d.schemas.code import FunctionCrystal
    crystals = [FunctionCrystal.from_dict(f.to_dict()) for f in functions]

Teaching:
    gotcha: AST nodes have line numbers but not byte offsets. We use
            lineno and end_lineno attributes. Line numbers are 1-indexed.
            (Evidence: ast module documentation)

    gotcha: Nested functions create scoping issues. A function inside
            a function has qualified_name "outer.inner", but a method
            inside a class has qualified_name "ClassName.method_name".
            We use different separators: "." for classes, "." for nested.
            (Evidence: PEP 8 naming conventions)

    gotcha: Type annotations can be complex expressions (Union[X, Y],
            list[dict[str, int]], etc.). We convert to string using
            ast.unparse() which is available in Python 3.9+.
            (Evidence: ast.unparse added in Python 3.9)

    gotcha: Lambda expressions are functions but rarely worth tracking
            as crystals. We skip them by checking isinstance(node, ast.FunctionDef).
            Lambda nodes are ast.Lambda, not ast.FunctionDef.
            (Evidence: ast module node types)
"""

from __future__ import annotations

import ast
import hashlib
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents.d.schemas.code import ParamInfo

# =============================================================================
# Function Info (Intermediate Structure)
# =============================================================================


@dataclass
class FunctionInfo:
    """
    Intermediate function metadata before crystallization.

    This is what the parser extracts from AST. It becomes a FunctionCrystal
    once we add proof/verification metadata and store it.

    Attributes:
        qualified_name: Fully qualified name (module.Class.method or module.function)
        file_path: Absolute path to source file
        line_range: (start_line, end_line) inclusive
        signature: Function signature as string (def name(params) -> return:)
        docstring: Docstring if present
        parameters: List of parameter info
        return_type: Return type annotation as string, if present
        decorators: List of decorator names
        is_async: Whether this is an async function
        is_method: Whether this is a method (inside a class)
        class_name: Class name if this is a method
        body_hash: SHA-256 hash of function body for change detection
        calls: Set of called function names (for call graph)
        imports: Set of imported module/symbol names
    """

    qualified_name: str
    file_path: str
    line_range: tuple[int, int]
    signature: str
    docstring: str | None = None
    parameters: list[ParamInfo] = field(default_factory=list)
    return_type: str | None = None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    class_name: str | None = None
    body_hash: str = ""
    calls: set[str] = field(default_factory=set)
    imports: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for FunctionCrystal creation."""
        return {
            "qualified_name": self.qualified_name,
            "file_path": self.file_path,
            "line_range": self.line_range,
            "signature": self.signature,
            "docstring": self.docstring,
            "parameters": [
                {
                    "name": p.name,
                    "type_annotation": p.type_annotation,
                    "default": p.default,
                    "is_variadic": p.is_variadic,
                    "is_keyword": p.is_keyword,
                }
                for p in self.parameters
            ],
            "return_type": self.return_type,
            "decorators": self.decorators,
            "is_async": self.is_async,
            "is_method": self.is_method,
            "class_name": self.class_name,
            "body_hash": self.body_hash,
            "calls": list(self.calls),
            "imports": list(self.imports),
        }


# =============================================================================
# Parser Implementation
# =============================================================================


class PythonFunctionParser:
    """
    Parser for extracting function metadata from Python source files.

    This parser uses Python's ast module to extract:
    - Function definitions (including methods)
    - Signatures with type annotations
    - Docstrings
    - Call graphs
    - Import statements

    Key guarantees:
    - Handles nested functions and class methods
    - Preserves type annotations
    - Computes stable body hashes
    - Gracefully handles malformed Python
    """

    def __init__(self, module_name: str | None = None):
        """
        Initialize the parser.

        Args:
            module_name: Optional module name for qualified names
                        (e.g., "agents.d.galois" for qualified_name prefix)
        """
        self.module_name = module_name
        self._imports: set[str] = set()

    def parse_file(self, file_path: str | Path) -> list[FunctionInfo]:
        """
        Parse a Python file and extract all function definitions.

        Args:
            file_path: Path to Python source file

        Returns:
            List of FunctionInfo objects for all functions in the file

        Raises:
            SyntaxError: If the file contains invalid Python syntax
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source = file_path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            raise SyntaxError(f"Failed to parse {file_path}: {e}") from e

        # Extract imports first
        self._imports = self._extract_imports(tree)

        # Walk the tree and extract functions
        functions: list[FunctionInfo] = []
        self._walk_tree(tree, functions, str(file_path.absolute()), source)

        return functions

    def _extract_imports(self, tree: ast.Module) -> set[str]:
        """
        Extract all import statements from the AST.

        Args:
            tree: AST module

        Returns:
            Set of imported module/symbol names
        """
        imports: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                for alias in node.names:
                    if node.module:
                        imports.add(f"{node.module}.{alias.name}")
                    else:
                        imports.add(alias.name)

        return imports

    def _walk_tree(
        self,
        node: ast.AST,
        functions: list[FunctionInfo],
        file_path: str,
        source: str,
        parent_name: str = "",
        class_name: str | None = None,
    ) -> None:
        """
        Walk the AST and extract function definitions.

        Args:
            node: Current AST node
            functions: List to append FunctionInfo objects to
            file_path: Absolute path to source file
            source: Full source code (for body hash computation)
            parent_name: Qualified name of parent (for nested functions)
            class_name: Name of enclosing class (for methods)
        """
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                # Recursively walk class body for methods
                self._walk_tree(
                    child,
                    functions,
                    file_path,
                    source,
                    parent_name=child.name,
                    class_name=child.name,
                )
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract function info
                func_info = self._extract_function(
                    child,
                    file_path,
                    source,
                    parent_name,
                    class_name,
                )
                functions.append(func_info)

                # Recursively walk function body for nested functions
                nested_parent = func_info.qualified_name
                self._walk_tree(
                    child,
                    functions,
                    file_path,
                    source,
                    parent_name=nested_parent,
                    class_name=None,  # Nested functions are not methods
                )
            else:
                # Continue walking
                self._walk_tree(child, functions, file_path, source, parent_name, class_name)

    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        source: str,
        parent_name: str,
        class_name: str | None,
    ) -> FunctionInfo:
        """
        Extract metadata from a function definition node.

        Args:
            node: Function definition AST node
            file_path: Absolute path to source file
            source: Full source code
            parent_name: Qualified name of parent
            class_name: Name of enclosing class (if method)

        Returns:
            FunctionInfo with extracted metadata
        """
        # Build qualified name
        if parent_name:
            qualified_name = f"{parent_name}.{node.name}"
        elif self.module_name:
            qualified_name = f"{self.module_name}.{node.name}"
        else:
            qualified_name = node.name

        # Extract line range
        line_range = (node.lineno, node.end_lineno or node.lineno)

        # Extract signature
        signature = self._signature_to_string(node)

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Extract parameters
        parameters = self._extract_parameters(node)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Extract decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]

        # Compute body hash
        body_hash = self._compute_body_hash(node, source)

        # Extract calls
        calls = self._extract_calls(node)

        return FunctionInfo(
            qualified_name=qualified_name,
            file_path=file_path,
            line_range=line_range,
            signature=signature,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=class_name is not None,
            class_name=class_name,
            body_hash=body_hash,
            calls=calls,
            imports=self._imports.copy(),
        )

    def _signature_to_string(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """
        Convert function definition to signature string.

        Args:
            node: Function definition AST node

        Returns:
            Signature string (e.g., "def foo(x: int, y: str = 'bar') -> bool")
        """
        # Build parameter list
        args = node.args
        params: list[str] = []

        # Positional-only parameters (Python 3.8+)
        if args.posonlyargs:
            for arg in args.posonlyargs:
                param_str = arg.arg
                if arg.annotation:
                    param_str += f": {ast.unparse(arg.annotation)}"
                params.append(param_str)
            params.append("/")

        # Regular parameters
        defaults_offset = len(args.args) - len(args.defaults)
        for i, arg in enumerate(args.args):
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {ast.unparse(arg.annotation)}"
            # Check if this parameter has a default
            default_idx = i - defaults_offset
            if default_idx >= 0:
                default_val = ast.unparse(args.defaults[default_idx])
                param_str += f" = {default_val}"
            params.append(param_str)

        # *args
        if args.vararg:
            param_str = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                param_str += f": {ast.unparse(args.vararg.annotation)}"
            params.append(param_str)

        # Keyword-only parameters
        for i, arg in enumerate(args.kwonlyargs):
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {ast.unparse(arg.annotation)}"
            # kw_defaults is aligned with kwonlyargs
            if args.kw_defaults[i] is not None:
                default_val = ast.unparse(args.kw_defaults[i])
                param_str += f" = {default_val}"
            params.append(param_str)

        # **kwargs
        if args.kwarg:
            param_str = f"**{args.kwarg.arg}"
            if args.kwarg.annotation:
                param_str += f": {ast.unparse(args.kwarg.annotation)}"
            params.append(param_str)

        # Build full signature
        param_str = ", ".join(params)
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        sig = f"{prefix} {node.name}({param_str})"

        # Add return type
        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"

        return sig

    def _extract_parameters(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ParamInfo]:
        """
        Extract parameter information from function definition.

        Args:
            node: Function definition AST node

        Returns:
            List of ParamInfo objects
        """
        params: list[ParamInfo] = []
        args = node.args

        # Regular parameters
        defaults_offset = len(args.args) - len(args.defaults)
        for i, arg in enumerate(args.args):
            type_annotation = None
            if arg.annotation:
                type_annotation = ast.unparse(arg.annotation)

            default = None
            default_idx = i - defaults_offset
            if default_idx >= 0:
                default = ast.unparse(args.defaults[default_idx])

            params.append(
                ParamInfo(
                    name=arg.arg,
                    type_annotation=type_annotation,
                    default=default,
                    is_variadic=False,
                    is_keyword=False,
                )
            )

        # *args
        if args.vararg:
            type_annotation = None
            if args.vararg.annotation:
                type_annotation = ast.unparse(args.vararg.annotation)

            params.append(
                ParamInfo(
                    name=args.vararg.arg,
                    type_annotation=type_annotation,
                    default=None,
                    is_variadic=True,
                    is_keyword=False,
                )
            )

        # Keyword-only parameters
        for i, arg in enumerate(args.kwonlyargs):
            type_annotation = None
            if arg.annotation:
                type_annotation = ast.unparse(arg.annotation)

            default = None
            if args.kw_defaults[i] is not None:
                default = ast.unparse(args.kw_defaults[i])

            params.append(
                ParamInfo(
                    name=arg.arg,
                    type_annotation=type_annotation,
                    default=default,
                    is_variadic=False,
                    is_keyword=False,
                )
            )

        # **kwargs
        if args.kwarg:
            type_annotation = None
            if args.kwarg.annotation:
                type_annotation = ast.unparse(args.kwarg.annotation)

            params.append(
                ParamInfo(
                    name=args.kwarg.arg,
                    type_annotation=type_annotation,
                    default=None,
                    is_variadic=False,
                    is_keyword=True,
                )
            )

        return params

    def _compute_body_hash(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source: str,
    ) -> str:
        """
        Compute SHA-256 hash of function body.

        This hash is used for change detection. If the body hash changes,
        the function has been modified.

        Args:
            node: Function definition AST node
            source: Full source code

        Returns:
            SHA-256 hash as hex string
        """
        # Extract function body source
        # We use ast.get_source_segment if available (Python 3.8+)
        try:
            # Get just the body (skip decorators and signature)
            body_nodes = node.body
            if not body_nodes:
                return hashlib.sha256(b"").hexdigest()

            # Use line numbers to extract body from source
            first_line = body_nodes[0].lineno
            last_line = body_nodes[-1].end_lineno or body_nodes[-1].lineno

            # Extract lines
            lines = source.splitlines(keepends=True)
            # Convert to 0-indexed
            body_lines = lines[first_line - 1 : last_line]
            body_source = "".join(body_lines)

            # Normalize whitespace for stable hashing
            # (so indentation changes don't change hash)
            normalized = inspect.cleandoc(body_source)

            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        except Exception:
            # Fallback: hash the entire function source
            try:
                func_source = ast.unparse(node)
                return hashlib.sha256(func_source.encode("utf-8")).hexdigest()
            except Exception:
                return hashlib.sha256(b"").hexdigest()

    def _extract_calls(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
        """
        Extract all function calls within a function.

        Args:
            node: Function definition AST node

        Returns:
            Set of called function names
        """
        calls: set[str] = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Extract the function name
                func_name = self._get_call_name(child.func)
                if func_name:
                    calls.add(func_name)

        return calls

    def _get_call_name(self, node: ast.expr) -> str | None:
        """
        Extract function name from a call expression.

        Args:
            node: Call expression AST node

        Returns:
            Function name as string, or None if can't determine
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Build qualified name: obj.attr
            obj_name = self._get_call_name(node.value)
            if obj_name:
                return f"{obj_name}.{node.attr}"
            else:
                return node.attr
        else:
            # Can't determine name for complex expressions
            return None


# =============================================================================
# Convenience Functions
# =============================================================================


def parse_file(file_path: str | Path, module_name: str | None = None) -> list[FunctionInfo]:
    """
    Parse a Python file and extract all function definitions.

    Args:
        file_path: Path to Python source file
        module_name: Optional module name for qualified names

    Returns:
        List of FunctionInfo objects

    Raises:
        SyntaxError: If the file contains invalid Python
        FileNotFoundError: If the file doesn't exist

    Usage:
        functions = parse_file("agents/d/galois.py", module_name="agents.d.galois")
        for func in functions:
            print(func.qualified_name, func.signature)
    """
    parser = PythonFunctionParser(module_name=module_name)
    return parser.parse_file(file_path)


def extract_imports(file_path: str | Path) -> set[str]:
    """
    Extract all import statements from a Python file.

    Args:
        file_path: Path to Python source file

    Returns:
        Set of imported module/symbol names

    Raises:
        SyntaxError: If the file contains invalid Python
        FileNotFoundError: If the file doesn't exist
    """
    file_path = Path(file_path)
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    parser = PythonFunctionParser()
    return parser._extract_imports(tree)


def extract_calls(function_node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """
    Extract all function calls within a function.

    Args:
        function_node: Function definition AST node

    Returns:
        Set of called function names
    """
    parser = PythonFunctionParser()
    return parser._extract_calls(function_node)


def compute_body_hash(function_node: ast.FunctionDef | ast.AsyncFunctionDef, source: str) -> str:
    """
    Compute SHA-256 hash of function body.

    Args:
        function_node: Function definition AST node
        source: Full source code

    Returns:
        SHA-256 hash as hex string
    """
    parser = PythonFunctionParser()
    return parser._compute_body_hash(function_node, source)


def signature_to_string(function_node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Convert function definition to signature string.

    Args:
        function_node: Function definition AST node

    Returns:
        Signature string
    """
    parser = PythonFunctionParser()
    return parser._signature_to_string(function_node)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Data models
    "FunctionInfo",
    # Parser
    "PythonFunctionParser",
    # Convenience functions
    "parse_file",
    "extract_imports",
    "extract_calls",
    "compute_body_hash",
    "signature_to_string",
]
