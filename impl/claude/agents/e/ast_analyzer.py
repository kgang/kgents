"""
AST Analyzer Agent: Static analysis of Python modules for targeted improvements.

Transforms Python source code into structured code analysis, identifying:
- Classes and their methods
- Functions and their complexity
- Import patterns
- Improvement targets

This agent enables targeted hypothesis generation instead of generic
"improve this file" suggestions.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from bootstrap.types import Agent


@dataclass(frozen=True)
class CodeStructure:
    """
    Extracted structure of a Python module.

    Contains AST-derived information about the module's composition,
    enabling targeted improvement suggestions.
    """
    module_name: str
    classes: tuple[dict[str, Any], ...]  # Immutable tuple for hashability
    functions: tuple[dict[str, Any], ...]
    imports: tuple[str, ...]
    docstring: Optional[str]
    line_count: int
    complexity_hints: tuple[str, ...]

    @classmethod
    def from_lists(
        cls,
        module_name: str,
        classes: list[dict[str, Any]],
        functions: list[dict[str, Any]],
        imports: list[str],
        docstring: Optional[str],
        line_count: int,
        complexity_hints: list[str],
    ) -> "CodeStructure":
        """Create CodeStructure from mutable lists (converts to tuples)."""
        return cls(
            module_name=module_name,
            classes=tuple(classes),
            functions=tuple(functions),
            imports=tuple(imports),
            docstring=docstring,
            line_count=line_count,
            complexity_hints=tuple(complexity_hints),
        )


@dataclass(frozen=True)
class ASTAnalysisInput:
    """Input for AST analysis."""
    path: Path
    source: Optional[str] = None  # If provided, use this instead of reading file


@dataclass(frozen=True)
class ASTAnalysisOutput:
    """Output from AST analysis."""
    structure: Optional[CodeStructure]
    error: Optional[str] = None
    targeted_hypotheses: tuple[str, ...] = ()


def analyze_module_ast(path: Path, source: Optional[str] = None) -> Optional[CodeStructure]:
    """
    Parse a Python module and extract its structure.

    Returns detailed information about classes, functions, and potential
    improvement targets.

    Args:
        path: Path to the Python file
        source: Optional source code (if None, reads from path)

    Returns:
        CodeStructure if parsing succeeds, None otherwise
    """
    try:
        if source is None:
            with open(path) as f:
                source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return None

    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    imports: list[str] = []
    complexity_hints: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                {
                    "name": m.name,
                    "args": len(m.args.args),
                    "lineno": m.lineno,
                    "is_async": isinstance(m, ast.AsyncFunctionDef),
                }
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "methods": methods,
                "method_count": len(methods),
                "bases": [ast.unparse(b) for b in node.bases] if node.bases else [],
            })

            # Complexity hint: large classes
            if len(methods) > 10:
                complexity_hints.append(
                    f"Class {node.name} has {len(methods)} methods - consider splitting"
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip methods (already captured in classes)
            if any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                parent_is_class = False
                for cls in ast.walk(tree):
                    if isinstance(cls, ast.ClassDef) and node in ast.walk(cls):
                        parent_is_class = True
                        break
                if parent_is_class:
                    continue

            func_info = {
                "name": node.name,
                "lineno": node.lineno,
                "args": [a.arg for a in node.args.args],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "is_private": node.name.startswith("_"),
            }
            functions.append(func_info)

            # Complexity hint: long functions
            if hasattr(node, 'end_lineno') and node.end_lineno:
                length = node.end_lineno - node.lineno
                if length > 50:
                    complexity_hints.append(
                        f"Function {node.name} is {length} lines - consider refactoring"
                    )

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            else:
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

    # Module-level docstring
    docstring: Optional[str] = None
    if (tree.body and
        isinstance(tree.body[0], ast.Expr) and
        isinstance(tree.body[0].value, ast.Constant)):
        raw_docstring = tree.body[0].value.value
        if isinstance(raw_docstring, str):
            docstring = raw_docstring[:200]

    return CodeStructure.from_lists(
        module_name=path.stem,
        classes=classes,
        functions=functions,
        imports=imports,
        docstring=docstring,
        line_count=len(source.splitlines()),
        complexity_hints=complexity_hints,
    )


def generate_targeted_hypotheses(
    structure: CodeStructure,
    max_targets: int = 3
) -> list[str]:
    """
    Generate targeted improvement hypotheses based on AST analysis.

    Instead of generic "improve this file", generates specific hypotheses
    like "Refactor the _extract_code method to reduce complexity".

    Args:
        structure: The analyzed code structure
        max_targets: Maximum number of hypotheses to generate

    Returns:
        List of targeted improvement hypotheses
    """
    hypotheses: list[str] = []

    # Target large classes
    for cls in structure.classes:
        if cls["method_count"] > 8:
            hypotheses.append(
                f"Refactor class {cls['name']} ({cls['method_count']} methods) - "
                f"consider extracting cohesive method groups into separate classes"
            )
        if not cls["bases"]:
            hypotheses.append(
                f"Review class {cls['name']} - should it inherit from a Protocol or ABC?"
            )

    # Target complex functions
    for func in structure.functions:
        if len(func["args"]) > 5:
            hypotheses.append(
                f"Function {func['name']} has {len(func['args'])} parameters - "
                f"consider using a dataclass to group related arguments"
            )
        if func["is_private"] and not func["name"].startswith("__"):
            hypotheses.append(
                f"Private function {func['name']} - is it tested? Consider adding test cases"
            )

    # Add complexity hints as hypotheses
    for hint in structure.complexity_hints[:2]:
        hypotheses.append(hint)

    # Generic but structure-aware hypotheses
    if len(structure.imports) > 15:
        hypotheses.append(
            f"Module has {len(structure.imports)} imports - review for unused imports"
        )

    if structure.line_count > 400:
        hypotheses.append(
            f"Module is {structure.line_count} lines - consider splitting into submodules"
        )

    return hypotheses[:max_targets]


class ASTAnalyzer(Agent[ASTAnalysisInput, ASTAnalysisOutput]):
    """
    Agent that analyzes Python source code structure.

    Morphism: ASTAnalysisInput → ASTAnalysisOutput

    Usage:
        analyzer = ASTAnalyzer()
        result = await analyzer.invoke(ASTAnalysisInput(path=Path("module.py")))
        if result.structure:
            for hint in result.targeted_hypotheses:
                print(f"  - {hint}")
    """

    def __init__(self, max_hypothesis_targets: int = 3):
        self._max_targets = max_hypothesis_targets

    @property
    def name(self) -> str:
        return "ASTAnalyzer"

    async def invoke(self, input: ASTAnalysisInput) -> ASTAnalysisOutput:
        """Analyze a Python module and return its structure."""
        try:
            structure = analyze_module_ast(input.path, input.source)
            if structure is None:
                return ASTAnalysisOutput(
                    structure=None,
                    error=f"Failed to parse {input.path}",
                )

            hypotheses = generate_targeted_hypotheses(structure, self._max_targets)

            return ASTAnalysisOutput(
                structure=structure,
                targeted_hypotheses=tuple(hypotheses),
            )
        except Exception as e:
            return ASTAnalysisOutput(
                structure=None,
                error=str(e),
            )


# Convenience factory
def ast_analyzer(max_targets: int = 3) -> ASTAnalyzer:
    """Create an AST analyzer agent."""
    return ASTAnalyzer(max_hypothesis_targets=max_targets)
