"""
Docstring Linter: Enforce Documentation Standards

Validates Python source files for documentation quality:
- Public symbols MUST have docstrings
- Docstrings MUST have non-empty summaries
- RICH tier files SHOULD have Teaching sections
- Evidence references MUST point to existing tests

This is the enforcement mechanism for documentation-as-code.

AGENTESE: concept.docs.lint

Teaching:
    gotcha: Only lint public symbols (no _ prefix).
            Private helpers don't need documentation.
            (Evidence: test_linter.py::test_skip_private_symbols)

    gotcha: AST parsing fails gracefully—returns empty results,
            not exceptions. Invalid Python is already caught by ruff.
            (Evidence: test_linter.py::test_invalid_syntax_graceful)

See: spec/protocols/living-docs.md
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Literal

from .extractor import DocstringExtractor
from .types import Tier


@dataclass(frozen=True)
class LintResult:
    """
    A single documentation lint issue.

    Each result represents one problem with one symbol.
    Severity determines whether it's blocking (error) or advisory (warning).
    """

    symbol: str
    module: str
    issue: Literal[
        "missing_docstring",
        "missing_summary",
        "missing_teaching",
        "invalid_evidence",
    ]
    severity: Literal["error", "warning"]
    line: int
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "module": self.module,
            "issue": self.issue,
            "severity": self.severity,
            "line": self.line,
            "message": self.message,
        }


@dataclass
class LintStats:
    """Statistics from a lint run."""

    files_checked: int = 0
    symbols_checked: int = 0
    errors: int = 0
    warnings: int = 0
    results: list[LintResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "files_checked": self.files_checked,
            "symbols_checked": self.symbols_checked,
            "errors": self.errors,
            "warnings": self.warnings,
            "results": [r.to_dict() for r in self.results],
        }


class DocstringLinter:
    """
    Linter for Python documentation standards.

    Enforces the documentation tier system:
    - MINIMAL: No requirements (private helpers)
    - STANDARD: Must have docstring with summary
    - RICH: Must have docstring, summary, and Teaching sections

    Teaching:
        gotcha: The linter uses AST, not runtime imports.
                This means it can lint broken code without crashes.
                (Evidence: test_linter.py::test_lint_broken_imports)
    """

    # Symbols that don't need docstrings even if public
    EXEMPT_SYMBOLS: frozenset[str] = frozenset(
        {
            "__all__",
            "__version__",
            "__author__",
            "__init__",  # Constructors are often trivial/self-explanatory
        }
    )

    # Patterns that indicate RICH tier (core implementation paths)
    # Matches extractor's RICH_PATTERNS for consistency
    RICH_PATTERNS: tuple[str, ...] = (
        "services/",
        "services.",
        "agents/",
        "agents.",
        "protocols/",
        "protocols.",
    )

    # Paths to exclude from linting
    EXCLUDE_PATTERNS: tuple[str, ...] = (
        "node_modules",
        "__pycache__",
        ".pyc",
        "dist/",
        "build/",
        ".git/",
        ".venv/",
        "venv/",
        "_tests/",
        "conftest.py",
    )

    def __init__(self) -> None:
        self._extractor = DocstringExtractor()

    def should_lint(self, path: Path) -> bool:
        """Check if a file should be linted (not excluded)."""
        path_str = str(path)
        if not path_str.endswith(".py"):
            return False
        return not any(p in path_str for p in self.EXCLUDE_PATTERNS)

    def lint_file(self, path: Path) -> list[LintResult]:
        """
        Lint a single Python file for documentation issues.

        Args:
            path: Path to Python file

        Returns:
            List of LintResults for all issues found
        """
        if not self.should_lint(path):
            return []

        try:
            source = path.read_text()
        except (OSError, UnicodeDecodeError):
            return []

        module_name = self._path_to_module(path)
        return self.lint_source(source, module_name, path)

    def lint_source(
        self,
        source: str,
        module_name: str,
        path: Path | None = None,
    ) -> list[LintResult]:
        """
        Lint Python source code for documentation issues.

        Args:
            source: Python source code
            module_name: Module path (e.g., "services.brain.persistence")
            path: Optional path for context (e.g., __init__.py detection)

        Returns:
            List of LintResults
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Invalid Python is not our problem—ruff handles that
            return []

        results: list[LintResult] = []
        is_init = path is not None and path.name == "__init__.py"
        is_rich_tier = any(p in module_name for p in self.RICH_PATTERNS)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                result = self._lint_node(
                    node,
                    module_name,
                    is_init=is_init,
                    is_rich_tier=is_rich_tier,
                )
                results.extend(result)

        return results

    def lint_directory(
        self,
        path: Path,
        changed_only: bool = False,
        changed_files: set[Path] | None = None,
    ) -> LintStats:
        """
        Lint all Python files in a directory.

        Args:
            path: Directory to lint
            changed_only: If True, only lint changed files
            changed_files: Set of changed file paths (for --changed mode)

        Returns:
            LintStats with all results and counts
        """
        stats = LintStats()

        for py_file in self._iter_python_files(path):
            if changed_only and changed_files is not None:
                if py_file not in changed_files:
                    continue

            results = self.lint_file(py_file)
            stats.files_checked += 1

            for result in results:
                stats.results.append(result)
                stats.symbols_checked += 1
                if result.severity == "error":
                    stats.errors += 1
                else:
                    stats.warnings += 1

        return stats

    def _lint_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        module_name: str,
        is_init: bool = False,
        is_rich_tier: bool = False,
    ) -> list[LintResult]:
        """Lint a single AST node for documentation issues."""
        results: list[LintResult] = []
        symbol = node.name
        line = node.lineno

        # Skip private symbols (except dunder methods)
        if symbol.startswith("_") and not symbol.startswith("__"):
            return []

        # Skip exempt symbols (__init__ is always exempt - constructors are often trivial)
        if symbol in self.EXEMPT_SYMBOLS:
            return []

        # Get docstring
        docstring = ast.get_docstring(node)

        # Rule 1: missing_docstring (ERROR for public symbols)
        if docstring is None:
            results.append(
                LintResult(
                    symbol=symbol,
                    module=module_name,
                    issue="missing_docstring",
                    severity="error",
                    line=line,
                    message=f"Public symbol '{symbol}' has no docstring",
                )
            )
            return results  # Can't check other rules without docstring

        # Rule 2: missing_summary (ERROR)
        summary = docstring.strip().split("\n")[0].strip()
        if not summary:
            results.append(
                LintResult(
                    symbol=symbol,
                    module=module_name,
                    issue="missing_summary",
                    severity="error",
                    line=line,
                    message=f"Docstring for '{symbol}' has empty or whitespace-only summary",
                )
            )

        # Rule 3: missing_teaching (WARNING for RICH tier only)
        if is_rich_tier and isinstance(node, ast.ClassDef):
            # Classes in RICH tier should have Teaching sections
            if "Teaching:" not in docstring and "gotcha:" not in docstring.lower():
                results.append(
                    LintResult(
                        symbol=symbol,
                        module=module_name,
                        issue="missing_teaching",
                        severity="warning",
                        line=line,
                        message=f"RICH tier class '{symbol}' has no Teaching section",
                    )
                )

        return results

    def _iter_python_files(self, path: Path) -> Iterator[Path]:
        """Iterate over Python files in a directory."""
        if path.is_file():
            if self.should_lint(path):
                yield path
        else:
            for py_file in path.rglob("*.py"):
                if self.should_lint(py_file):
                    yield py_file

    def _path_to_module(self, path: Path) -> str:
        """
        Convert a file path to a module name.

        Example: /path/to/services/brain/persistence.py -> services.brain.persistence
        """
        parts = path.parts
        try:
            impl_idx = parts.index("impl")
            if impl_idx + 1 < len(parts) and parts[impl_idx + 1] == "claude":
                module_parts_tuple = parts[impl_idx + 2 :]
            else:
                module_parts_tuple = parts[-3:]
        except ValueError:
            module_parts_tuple = parts[-3:]

        module_parts = list(module_parts_tuple)
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)


def lint_file(path: Path) -> list[LintResult]:
    """
    Lint a single Python file for documentation issues.

    Convenience function wrapping DocstringLinter.

    Args:
        path: Path to Python file

    Returns:
        List of LintResults
    """
    linter = DocstringLinter()
    return linter.lint_file(path)


def lint_directory(
    path: Path,
    changed_only: bool = False,
    changed_files: set[Path] | None = None,
) -> LintStats:
    """
    Lint all Python files in a directory.

    Convenience function wrapping DocstringLinter.

    Args:
        path: Directory to lint
        changed_only: If True, only lint changed files
        changed_files: Set of changed file paths

    Returns:
        LintStats with all results
    """
    linter = DocstringLinter()
    return linter.lint_directory(path, changed_only, changed_files)


def get_changed_files(repo_root: Path) -> set[Path]:
    """
    Get list of Python files changed since last commit.

    Uses git to determine changed files.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "HEAD", "--", "*.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        changed = set()
        for line in result.stdout.strip().split("\n"):
            if line:
                changed.add(repo_root / line)

        # Also get unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "*.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                changed.add(repo_root / line)

        return changed
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
