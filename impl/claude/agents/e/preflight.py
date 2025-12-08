"""
Pre-Flight Checker: Validate module health before evolution.

This module implements pre-flight checks to avoid wasting LLM calls
on modules with fundamental issues that would prevent successful evolution.

Part of Layer 1 (Prompt Engineering) - provides error-aware context.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from bootstrap.types import Agent

from .experiment import CodeModule


@dataclass(frozen=True)
class PreFlightReport:
    """
    Report from pre-flight checks.

    Indicates whether module is ready for evolution and what
    issues need attention.
    """
    can_evolve: bool
    blocking_issues: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    baseline_error_count: int = 0
    recommendations: tuple[str, ...] = ()

    @classmethod
    def from_lists(
        cls,
        can_evolve: bool,
        blocking_issues: list[str] = None,
        warnings: list[str] = None,
        baseline_error_count: int = 0,
        recommendations: list[str] = None,
    ) -> PreFlightReport:
        """Create PreFlightReport from mutable lists."""
        return cls(
            can_evolve=can_evolve,
            blocking_issues=tuple(blocking_issues or []),
            warnings=tuple(warnings or []),
            baseline_error_count=baseline_error_count,
            recommendations=tuple(recommendations or []),
        )


@dataclass(frozen=True)
class PreFlightInput:
    """Input for pre-flight checking."""
    module: CodeModule


class PreFlightChecker(Agent[PreFlightInput, PreFlightReport]):
    """
    Check module health before attempting evolution.

    Prevents wasted LLM calls on modules with fundamental issues.

    Checks:
    1. Syntax validity (can parse with ast.parse)
    2. Pre-existing type error count (baseline)
    3. Incomplete definitions (missing imports, etc.)
    4. Module complexity (too large to evolve safely)

    Morphism: PreFlightInput → PreFlightReport
    """

    def __init__(
        self,
        max_error_threshold: int = 15,
        max_line_threshold: int = 1000,
    ):
        """
        Initialize pre-flight checker.

        Args:
            max_error_threshold: Skip evolution if more than this many errors
            max_line_threshold: Warn if module exceeds this line count
        """
        self._max_error_threshold = max_error_threshold
        self._max_line_threshold = max_line_threshold

    @property
    def name(self) -> str:
        return "PreFlightChecker"

    async def invoke(self, input: PreFlightInput) -> PreFlightReport:
        """Run pre-flight checks on a module."""
        module = input.module
        issues: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Read module source
        try:
            source = module.path.read_text()
        except Exception as e:
            return PreFlightReport.from_lists(
                can_evolve=False,
                blocking_issues=[f"Cannot read file: {e}"],
            )

        # 1. Parse current code
        tree = self._check_syntax(source)
        if tree is None:
            return PreFlightReport.from_lists(
                can_evolve=False,
                blocking_issues=["BLOCKER: Syntax error prevents parsing"],
                recommendations=[
                    "Fix syntax errors manually before attempting evolution",
                    "Run: python -m py_compile " + str(module.path),
                ],
            )

        # 2. Check for pre-existing type errors
        type_errors = self._check_types(module.path)
        if len(type_errors) > self._max_error_threshold:
            return PreFlightReport.from_lists(
                can_evolve=False,
                blocking_issues=[
                    f"BLOCKER: {len(type_errors)} pre-existing type errors (threshold: {self._max_error_threshold})"
                ],
                recommendations=[
                    "Fix critical type errors manually first",
                    f"Run: mypy {module.path} --strict",
                ],
            )
        elif len(type_errors) > 5:
            warnings.append(f"⚠️ {len(type_errors)} pre-existing type errors")

        # 3. Check for incomplete definitions
        incomplete = self._find_incomplete_definitions(tree)
        if incomplete:
            warnings.extend(incomplete)

        # 4. Check for missing imports
        missing = self._find_missing_imports(tree, source)
        if missing:
            # Missing imports are usually blocking
            return PreFlightReport.from_lists(
                can_evolve=False,
                blocking_issues=[f"BLOCKER: Missing imports: {', '.join(missing)}"],
                recommendations=[
                    "Add missing imports manually",
                    "Verify import sources are available",
                ],
            )

        # 5. Check module size
        line_count = len(source.splitlines())
        if line_count > self._max_line_threshold:
            warnings.append(
                f"⚠️ Module is large ({line_count} lines) - evolution may be slow"
            )
            recommendations.append("Consider splitting into smaller modules")

        # 6. Check for incomplete generic types (common error)
        incomplete_generics = self._find_incomplete_generics(source)
        if incomplete_generics:
            warnings.append(
                f"⚠️ Found {len(incomplete_generics)} potentially incomplete generic types"
            )

        # All checks passed
        return PreFlightReport.from_lists(
            can_evolve=True,
            warnings=warnings,
            baseline_error_count=len(type_errors),
            recommendations=recommendations,
        )

    def _check_syntax(self, source: str) -> Optional[ast.Module]:
        """
        Check if source code is syntactically valid.

        Returns AST if valid, None if syntax error.
        """
        try:
            return ast.parse(source)
        except SyntaxError:
            return None

    def _check_types(self, path: Path) -> list[str]:
        """
        Check for type errors using mypy.

        Returns list of error messages.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", str(path), "--strict", "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                # Parse errors from mypy output
                errors = []
                for line in result.stdout.split("\n"):
                    if line.strip() and "error:" in line:
                        errors.append(line.strip())
                return errors

            return []

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If mypy not available, skip type checking
            return []

    def _find_incomplete_definitions(self, tree: ast.Module) -> list[str]:
        """
        Find incomplete class/function definitions.

        Returns list of issues found.
        """
        issues = []

        for node in ast.walk(tree):
            # Classes without proper initialization
            if isinstance(node, ast.ClassDef):
                has_init = any(
                    isinstance(n, ast.FunctionDef) and n.name == "__init__"
                    for n in node.body
                )

                has_dataclass = any(
                    isinstance(d, ast.Name) and d.id == "dataclass"
                    for d in node.decorator_list
                )

                # Check if class body is just 'pass'
                is_stub = (
                    len(node.body) == 1 and
                    isinstance(node.body[0], ast.Pass)
                )

                if is_stub:
                    issues.append(f"Class {node.name} is a stub (only contains 'pass')")

            # Functions with just 'pass'
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_stub = (
                    len(node.body) == 1 and
                    isinstance(node.body[0], ast.Pass)
                )

                if is_stub and not node.name.startswith("_"):
                    issues.append(f"Function {node.name} is a stub (only contains 'pass')")

        return issues

    def _find_missing_imports(self, tree: ast.Module, source: str) -> list[str]:
        """
        Find potentially missing imports.

        Checks for undefined names that look like they should be imported.
        """
        # Get all imported names
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

        # Get all defined names (classes, functions, variables)
        defined_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_names.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_names.add(node.id)

        # Get all used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Builtins to exclude
        builtins = {
            'int', 'str', 'float', 'bool', 'list', 'dict', 'tuple', 'set',
            'None', 'True', 'False', 'print', 'len', 'range', 'enumerate',
            'zip', 'map', 'filter', 'any', 'all', 'isinstance', 'type',
            'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
        }

        # Find potentially missing imports
        missing = []
        for name in used_names:
            if (name not in imported_names and
                name not in defined_names and
                name not in builtins and
                not name.startswith('_')):
                missing.append(name)

        return missing[:5]  # Limit to first 5

    def _find_incomplete_generics(self, source: str) -> list[str]:
        """
        Find potentially incomplete generic type annotations.

        Example: Maybe[ or Fix[A, or Agent[A,]
        """
        import re

        incomplete = []

        # Pattern 1: Unclosed brackets
        pattern1 = r'\b[A-Z]\w*\[\s*(?:[A-Z]\w*\s*,\s*)*$'
        matches = re.findall(pattern1, source, re.MULTILINE)
        incomplete.extend(matches)

        # Pattern 2: Trailing comma in generic
        pattern2 = r'\b([A-Z]\w*\[[A-Z]\w*\s*,\s*\])'
        matches = re.findall(pattern2, source)
        incomplete.extend(matches)

        return list(set(incomplete))  # Remove duplicates


# Convenience factory
def preflight_checker(
    max_error_threshold: int = 15,
    max_line_threshold: int = 1000,
) -> PreFlightChecker:
    """Create a pre-flight checker agent."""
    return PreFlightChecker(
        max_error_threshold=max_error_threshold,
        max_line_threshold=max_line_threshold,
    )
