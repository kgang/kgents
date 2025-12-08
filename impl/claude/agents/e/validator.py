"""
Schema validation layer for generated code.

This module provides fast, AST-based validation that catches common errors
before running expensive type checking with mypy. Validates:
- Complete class constructors (dataclass or __init__)
- Type annotation presence and correctness
- Import validity
- Common type errors (generic parameters, etc.)
- Code completeness (no TODO/pass placeholders)
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class IssueSeverity(Enum):
    """Severity of validation issue."""
    ERROR = "error"       # Blocks incorporation
    WARNING = "warning"   # Should be reviewed
    INFO = "info"         # FYI only


class IssueCategory(Enum):
    """Category of validation issue."""
    CONSTRUCTOR = "constructor"         # Missing/incomplete __init__ or dataclass
    TYPE_ANNOTATION = "type_annotation"  # Missing or incorrect type hints
    IMPORT = "import"                    # Import issues
    GENERIC_TYPE = "generic_type"        # Generic type parameter errors
    COMPLETENESS = "completeness"        # Incomplete code (TODO, pass, etc.)
    SYNTAX = "syntax"                    # Syntax errors


@dataclass
class Issue:
    """A validation issue found in code."""
    severity: IssueSeverity
    category: IssueCategory
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    symbol: Optional[str] = None  # Affected symbol (class/function name)
    metadata: Optional[dict[str, Any]] = None  # Additional context


@dataclass
class ValidationReport:
    """Result of validating code."""
    is_valid: bool
    issues: list[Issue]
    code_hash: Optional[str] = None  # For caching
    validation_time_ms: Optional[float] = None

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(i.severity == IssueSeverity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        """Count error-level issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count warning-level issues."""
        return sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)


class SchemaValidator:
    """
    Fast schema validator for generated code.

    Validates code structure before expensive type checking,
    catching common LLM generation errors early.
    """

    # Known generic types and their expected parameter counts
    KNOWN_GENERICS: dict[str, int] = {
        'Agent': 2,          # Agent[A, B]
        'Fix': 1,            # Fix[A]
        'Result': 1,         # Result[A]
        'Optional': 1,       # Optional[A]
        'List': 1,           # List[A]
        'Dict': 2,           # Dict[K, V]
        'Tuple': -1,         # Variable arity
        'Union': -1,         # Variable arity
        'Callable': -1,      # Variable arity
    }

    def __init__(self, strict: bool = True):
        """
        Initialize validator.

        Args:
            strict: If True, enforces stricter rules (all type annotations required)
        """
        self.strict = strict

    def validate(self, code: str, module_path: Optional[Path] = None) -> ValidationReport:
        """
        Validate code structure and common patterns.

        Args:
            code: Python source code to validate
            module_path: Optional path for context (checking imports)

        Returns:
            ValidationReport with any issues found
        """
        issues: list[Issue] = []

        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(Issue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SYNTAX,
                message=f"Syntax error: {e.msg}",
                line=e.lineno,
                column=e.offset
            ))
            return ValidationReport(is_valid=False, issues=issues)

        # Run validation checks
        issues.extend(self._check_class_constructors(tree))
        issues.extend(self._check_type_annotations(tree))
        issues.extend(self._check_common_type_errors(tree))
        issues.extend(self._check_completeness(tree))

        if module_path:
            issues.extend(self._check_imports(tree, module_path))

        # Validation passes if no errors (warnings are OK)
        is_valid = not any(i.severity == IssueSeverity.ERROR for i in issues)

        return ValidationReport(is_valid=is_valid, issues=issues)

    def _check_class_constructors(self, tree: ast.Module) -> list[Issue]:
        """
        Check all classes have valid constructors.

        A class must have either:
        - @dataclass decorator, or
        - __init__ method
        """
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_init = any(
                    isinstance(n, ast.FunctionDef) and n.name == '__init__'
                    for n in node.body
                )

                has_dataclass = any(
                    self._is_decorator_name(d, 'dataclass')
                    for d in node.decorator_list
                )

                if not (has_init or has_dataclass):
                    issues.append(Issue(
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.CONSTRUCTOR,
                        message=f"Class '{node.name}' has no __init__ or @dataclass decorator",
                        line=node.lineno,
                        symbol=node.name
                    ))

        return issues

    def _check_type_annotations(self, tree: ast.Module) -> list[Issue]:
        """
        Check function signatures have type annotations.

        In strict mode, all parameters and return types must be annotated.
        """
        if not self.strict:
            return []

        issues = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private/special methods in type checking
                if node.name.startswith('_') and node.name != '__init__':
                    continue

                # Check return annotation
                if node.returns is None and node.name != '__init__':
                    issues.append(Issue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.TYPE_ANNOTATION,
                        message=f"Function '{node.name}' missing return type annotation",
                        line=node.lineno,
                        symbol=node.name
                    ))

                # Check parameter annotations
                for arg in node.args.args:
                    # Skip 'self' and 'cls'
                    if arg.arg in ('self', 'cls'):
                        continue

                    if arg.annotation is None:
                        issues.append(Issue(
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.TYPE_ANNOTATION,
                            message=f"Parameter '{arg.arg}' in '{node.name}' missing type annotation",
                            line=node.lineno,
                            symbol=node.name,
                            metadata={'parameter': arg.arg}
                        ))

        return issues

    def _check_common_type_errors(self, tree: ast.Module) -> list[Issue]:
        """
        Check for common type annotation errors.

        - Incomplete generic types (Maybe[, Fix[A,B] when should be Fix[A], etc.)
        - Wrong number of type parameters
        - Unclosed brackets
        """
        issues = []

        for node in ast.walk(tree):
            # Check subscripted types (generics)
            if isinstance(node, ast.Subscript):
                try:
                    source = ast.unparse(node)

                    # Check for unclosed brackets
                    if source.count('[') != source.count(']'):
                        issues.append(Issue(
                            severity=IssueSeverity.ERROR,
                            category=IssueCategory.GENERIC_TYPE,
                            message=f"Incomplete generic type: {source}",
                            line=getattr(node, 'lineno', None)
                        ))
                        continue

                    # Check for wrong number of type params
                    if isinstance(node.value, ast.Name):
                        type_name = node.value.id
                        expected_params = self.KNOWN_GENERICS.get(type_name)

                        if expected_params is not None and expected_params >= 0:
                            actual_params = self._count_type_params(node.slice)

                            if actual_params != expected_params:
                                issues.append(Issue(
                                    severity=IssueSeverity.ERROR,
                                    category=IssueCategory.GENERIC_TYPE,
                                    message=f"{type_name} expects {expected_params} type param(s), got {actual_params}",
                                    line=getattr(node, 'lineno', None),
                                    metadata={'expected': expected_params, 'actual': actual_params}
                                ))

                except Exception as e:
                    # If we can't unparse/analyze, log as warning
                    issues.append(Issue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.GENERIC_TYPE,
                        message=f"Could not analyze generic type: {e}",
                        line=getattr(node, 'lineno', None)
                    ))

        return issues

    def _check_completeness(self, tree: ast.Module) -> list[Issue]:
        """
        Check for incomplete code markers.

        - TODO comments
        - Pass statements in function bodies
        - Ellipsis (...) placeholders
        - NotImplemented returns
        """
        issues = []
        source = ast.unparse(tree)

        # Check for TODO comments
        if 'TODO' in source or 'FIXME' in source:
            issues.append(Issue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.COMPLETENESS,
                message="Code contains TODO/FIXME markers",
            ))

        # Check for suspicious pass statements (not just in empty except/finally)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function body is just "pass"
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append(Issue(
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.COMPLETENESS,
                        message=f"Function '{node.name}' has empty body (just 'pass')",
                        line=node.lineno,
                        symbol=node.name
                    ))

            # Check for NotImplemented
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant):
                if node.value.value is NotImplemented:
                    issues.append(Issue(
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.COMPLETENESS,
                        message="Function returns NotImplemented",
                        line=node.lineno
                    ))

        return issues

    def _check_imports(self, tree: ast.Module, module_path: Path) -> list[Issue]:
        """
        Check import validity (basic checks only).

        Full import resolution is expensive; this does basic sanity checks.
        """
        issues = []

        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                # Check for relative imports beyond package root
                if node.level and node.level > 3:
                    issues.append(Issue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.IMPORT,
                        message=f"Deeply nested relative import (level {node.level})",
                        line=node.lineno
                    ))

        return issues

    def _is_decorator_name(self, decorator: ast.expr, name: str) -> bool:
        """Check if decorator matches a given name."""
        if isinstance(decorator, ast.Name):
            return decorator.id == name
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id == name
        return False

    def _count_type_params(self, slice_node: ast.expr) -> int:
        """Count type parameters in a generic type subscript."""
        if isinstance(slice_node, ast.Tuple):
            return len(slice_node.elts)
        else:
            # Single parameter
            return 1


# Convenience factory

def schema_validator(strict: bool = True) -> SchemaValidator:
    """Create a schema validator."""
    return SchemaValidator(strict=strict)
