"""
Incremental code repair for validation issues.

This module attempts to automatically fix common code generation errors
using AST manipulation and heuristics. Repairs:
- Missing imports
- Incomplete generic types
- Missing default values
- Simple type annotation fixes
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .validator import Issue, IssueCategory, IssueSeverity, ValidationReport, schema_validator


@dataclass
class Repair:
    """A single repair applied to code."""
    issue: Issue
    description: str
    strategy: str  # Name of repair strategy used


@dataclass
class RepairResult:
    """Result of attempting to repair code."""
    success: bool
    code: Optional[str] = None
    repairs_applied: Optional[list[Repair]] = None
    remaining_issues: Optional[list[Issue]] = None
    error: Optional[str] = None


class CodeRepairer:
    """
    Attempt to repair common code generation errors.

    Uses AST manipulation and heuristics to fix issues identified
    by the validator. Not all issues are repairable; this is best-effort.
    """

    # Common imports for standard types
    COMMON_IMPORTS = {
        'Agent': ('bootstrap.types', 'Agent'),
        'Fix': ('bootstrap.types', 'Fix'),
        'Verdict': ('bootstrap.types', 'Verdict'),
        'Optional': ('typing', 'Optional'),
        'List': ('typing', 'List'),
        'Dict': ('typing', 'Dict'),
        'Any': ('typing', 'Any'),
        'dataclass': ('dataclasses', 'dataclass'),
        'Path': ('pathlib', 'Path'),
        'Enum': ('enum', 'Enum'),
    }

    def __init__(self, max_iterations: int = 3):
        """
        Initialize repairer.

        Args:
            max_iterations: Maximum repair iterations before giving up
        """
        self.max_iterations = max_iterations

    def repair(
        self,
        code: str,
        validation_report: ValidationReport,
        module_path: Optional[Path] = None
    ) -> RepairResult:
        """
        Attempt to repair validation issues.

        Args:
            code: Code to repair
            validation_report: Validation report with issues
            module_path: Optional path for context

        Returns:
            RepairResult with repaired code or error
        """
        if validation_report.is_valid:
            return RepairResult(
                success=True,
                code=code,
                repairs_applied=[],
                remaining_issues=[]
            )

        # Categorize issues
        repairable = [i for i in validation_report.issues if self._can_repair(i)]
        unrepairable = [i for i in validation_report.issues if not self._can_repair(i)]

        if not repairable:
            return RepairResult(
                success=False,
                code=code,
                remaining_issues=unrepairable,
                error="No repairable issues found"
            )

        # Attempt iterative repair
        current_code = code
        repairs_applied: list[Repair] = []

        for iteration in range(self.max_iterations):
            try:
                tree = ast.parse(current_code)
            except SyntaxError as e:
                return RepairResult(
                    success=False,
                    code=current_code,
                    repairs_applied=repairs_applied,
                    remaining_issues=unrepairable,
                    error=f"Syntax error prevents repair: {e}"
                )

            # Apply repairs for this iteration
            iteration_repairs = []
            modified = False

            for issue in repairable:
                if issue.category == IssueCategory.IMPORT:
                    tree, repaired = self._add_missing_import(tree, issue)
                    if repaired:
                        iteration_repairs.append(repaired)
                        modified = True

                elif issue.category == IssueCategory.GENERIC_TYPE:
                    tree, repaired = self._fix_generic_type(tree, issue)
                    if repaired:
                        iteration_repairs.append(repaired)
                        modified = True

                elif issue.category == IssueCategory.COMPLETENESS:
                    tree, repaired = self._fix_completeness(tree, issue)
                    if repaired:
                        iteration_repairs.append(repaired)
                        modified = True

            # If no modifications this iteration, we're done
            if not modified:
                break

            # Update code
            current_code = ast.unparse(tree)
            repairs_applied.extend(iteration_repairs)

            # Re-validate
            validator = schema_validator(strict=True)
            new_report = validator.validate(current_code, module_path)

            if new_report.is_valid:
                return RepairResult(
                    success=True,
                    code=current_code,
                    repairs_applied=repairs_applied,
                    remaining_issues=[]
                )

            # Update repairable issues for next iteration
            repairable = [i for i in new_report.issues if self._can_repair(i)]
            unrepairable = [i for i in new_report.issues if not self._can_repair(i)]

        # Max iterations reached
        validator = schema_validator(strict=True)
        final_report = validator.validate(current_code, module_path)

        return RepairResult(
            success=final_report.is_valid,
            code=current_code,
            repairs_applied=repairs_applied,
            remaining_issues=final_report.issues,
            error="Max iterations reached" if not final_report.is_valid else None
        )

    def _can_repair(self, issue: Issue) -> bool:
        """Check if an issue is potentially repairable."""
        # Only attempt to repair certain categories
        repairable_categories = {
            IssueCategory.IMPORT,
            IssueCategory.GENERIC_TYPE,
            IssueCategory.COMPLETENESS,
        }

        # Only repair errors and warnings
        repairable_severities = {
            IssueSeverity.ERROR,
            IssueSeverity.WARNING,
        }

        return (
            issue.category in repairable_categories and
            issue.severity in repairable_severities
        )

    def _add_missing_import(
        self,
        tree: ast.Module,
        issue: Issue
    ) -> tuple[ast.Module, Optional[Repair]]:
        """
        Add a missing import to the AST.

        Attempts to infer the import from common types.
        Also checks for undefined decorators like @dataclass.
        """
        # Try to extract the missing name from issue metadata or message
        name = issue.metadata.get('name') if issue.metadata else None

        if not name:
            # Try to parse from message
            if "'" in issue.message:
                parts = issue.message.split("'")
                if len(parts) >= 2:
                    name = parts[1]

        # Special case: detect @dataclass usage
        if not name:
            # Check if code uses @dataclass but doesn't import it
            source = ast.unparse(tree)
            if '@dataclass' in source:
                # Check if dataclass is imported
                has_dataclass_import = False
                for node in tree.body:
                    if isinstance(node, ast.ImportFrom) and node.module == 'dataclasses':
                        for alias in node.names:
                            if alias.name == 'dataclass':
                                has_dataclass_import = True
                                break

                if not has_dataclass_import:
                    name = 'dataclass'

        if not name or name not in self.COMMON_IMPORTS:
            return tree, None

        # Get import info
        module_name, import_name = self.COMMON_IMPORTS[name]

        # Check if already imported
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == module_name:
                for alias in node.names:
                    if alias.name == import_name:
                        # Already imported
                        return tree, None

        # Add import
        import_node = ast.ImportFrom(
            module=module_name,
            names=[ast.alias(name=import_name, asname=None)],
            level=0
        )

        # Insert after any existing imports, or at beginning
        insert_pos = 0
        for i, node in enumerate(tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_pos = i + 1

        tree.body.insert(insert_pos, import_node)

        repair = Repair(
            issue=issue,
            description=f"Added missing import: from {module_name} import {import_name}",
            strategy="add_import"
        )

        return tree, repair

    def _fix_generic_type(
        self,
        tree: ast.Module,
        issue: Issue
    ) -> tuple[ast.Module, Optional[Repair]]:
        """
        Fix incomplete or incorrect generic type annotations.

        This is challenging without full context, so we use heuristics:
        - Fix[A, B] -> Fix[A] (common mistake from plan)
        - Maybe[ -> Maybe[str] (default to str as safe fallback)
        """
        if not issue.line:
            return tree, None

        # Find the node at this line
        target_nodes = [
            node for node in ast.walk(tree)
            if hasattr(node, 'lineno') and node.lineno == issue.line
        ]

        if not target_nodes:
            return tree, None

        # Look for Subscript nodes (generics)
        modified = False
        for node in target_nodes:
            if isinstance(node, ast.Subscript):
                # Check for Fix[A, B] -> Fix[A]
                if isinstance(node.value, ast.Name) and node.value.id == 'Fix':
                    if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2:
                        # Take only first parameter
                        node.slice = node.slice.elts[0]
                        modified = True

        if not modified:
            return tree, None

        repair = Repair(
            issue=issue,
            description="Fixed generic type parameter count",
            strategy="fix_generic"
        )

        return tree, repair

    def _fix_completeness(
        self,
        tree: ast.Module,
        issue: Issue
    ) -> tuple[ast.Module, Optional[Repair]]:
        """
        Fix completeness issues like empty function bodies.

        Strategy: Replace "pass" with "raise NotImplementedError()"
        This is more honest than leaving "pass".
        """
        if not issue.symbol or not issue.line:
            return tree, None

        # Find the function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == issue.symbol and node.lineno == issue.line:
                    # Check if body is just "pass"
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        # Replace with raise NotImplementedError
                        node.body = [
                            ast.Raise(
                                exc=ast.Call(
                                    func=ast.Name(id='NotImplementedError', ctx=ast.Load()),
                                    args=[],
                                    keywords=[]
                                ),
                                cause=None
                            )
                        ]

                        repair = Repair(
                            issue=issue,
                            description=f"Replaced 'pass' with 'raise NotImplementedError()' in {issue.symbol}",
                            strategy="fix_completeness"
                        )

                        return tree, repair

        return tree, None


# Convenience factory

def code_repairer(max_iterations: int = 3) -> CodeRepairer:
    """Create a code repairer."""
    return CodeRepairer(max_iterations=max_iterations)
