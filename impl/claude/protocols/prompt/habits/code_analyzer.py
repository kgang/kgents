"""
Code Pattern Analyzer: Extract patterns from code AST analysis.

Part of Wave 4 of the Evergreen Prompt System.

Analyzes Python code for:
- Naming conventions (snake_case, camelCase)
- Type hint usage
- Docstring style
- Import patterns
- Class/function structure
"""

from __future__ import annotations

import ast
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .git_analyzer import GitPattern

logger = logging.getLogger(__name__)


class CodeAnalyzerError(Exception):
    """Error during code analysis."""

    pass


@dataclass(frozen=True)
class CodePattern:
    """A detected pattern from code analysis."""

    pattern_type: Literal["naming", "typing", "docstrings", "structure", "imports"]
    description: str
    confidence: float  # 0.0-1.0
    evidence: tuple[str, ...]
    details: dict[str, float]

    def __str__(self) -> str:
        return f"[{self.pattern_type}] {self.description} (confidence: {self.confidence:.0%})"

    def to_git_pattern(self) -> GitPattern:
        """Convert to GitPattern for unified handling."""
        # Map code pattern types to git pattern types
        type_map = {
            "naming": "commit_style",
            "typing": "commit_style",
            "docstrings": "commit_style",
            "structure": "file_focus",
            "imports": "file_focus",
        }
        return GitPattern(
            pattern_type=type_map.get(self.pattern_type, "commit_style"),
            description=self.description,
            confidence=self.confidence,
            evidence=self.evidence,
            details=self.details,
        )


@dataclass
class CodePatternAnalyzer:
    """
    Analyze Python code for style and structure patterns.

    Uses AST parsing to detect:
    - Naming conventions
    - Type annotation usage
    - Docstring presence and style
    - Import organization
    - Code structure (class vs function heavy)

    Thread-safe: all operations are stateless file reads.
    """

    repo_path: Path
    sample_size: int = 50  # Max files to analyze
    include_patterns: tuple[str, ...] = ("**/*.py",)
    exclude_patterns: tuple[str, ...] = (
        "**/_tests/**",
        "**/test_*.py",
        "**/*_test.py",
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**",
        "**/node_modules/**",
    )

    _analyzed_files: list[Path] = field(default_factory=list, init=False)

    def analyze(self) -> list[CodePattern]:
        """
        Extract patterns from Python code.

        Returns list of detected patterns, highest confidence first.
        """
        if not self.repo_path.exists():
            logger.warning(f"Repository path not found: {self.repo_path}")
            return []

        # Find Python files
        python_files = self._find_python_files()
        if not python_files:
            logger.info("No Python files found")
            return []

        self._analyzed_files = python_files[: self.sample_size]
        logger.info(f"Analyzing {len(self._analyzed_files)} Python files")

        patterns: list[CodePattern] = []

        try:
            pattern = self._analyze_naming_conventions()
            if pattern:
                patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Failed to analyze naming: {e}")

        try:
            pattern = self._analyze_type_hints()
            if pattern:
                patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Failed to analyze type hints: {e}")

        try:
            pattern = self._analyze_docstrings()
            if pattern:
                patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Failed to analyze docstrings: {e}")

        try:
            pattern = self._analyze_structure()
            if pattern:
                patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Failed to analyze structure: {e}")

        try:
            pattern = self._analyze_imports()
            if pattern:
                patterns.append(pattern)
        except Exception as e:
            logger.warning(f"Failed to analyze imports: {e}")

        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns

    def _find_python_files(self) -> list[Path]:
        """Find Python files, respecting include/exclude patterns."""
        files: list[Path] = []

        for pattern in self.include_patterns:
            for path in self.repo_path.glob(pattern):
                if path.is_file() and not self._is_excluded(path):
                    files.append(path)

        # Sort by modification time (most recent first) for sampling
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files

    def _is_excluded(self, path: Path) -> bool:
        """Check if path matches any exclude pattern."""
        rel_path = str(path.relative_to(self.repo_path))
        for pattern in self.exclude_patterns:
            # Simple glob matching
            if self._matches_pattern(rel_path, pattern):
                return True
        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Simple pattern matching (supports ** and *)."""
        # Convert glob pattern to regex
        regex = pattern.replace(".", r"\.")
        regex = regex.replace("**", "DOUBLESTAR")
        regex = regex.replace("*", "[^/]*")
        regex = regex.replace("DOUBLESTAR", ".*")
        regex = f"^{regex}$"
        return bool(re.match(regex, path))

    def _parse_file(self, path: Path) -> ast.Module | None:
        """Parse a Python file, returning None on error."""
        try:
            content = path.read_text(encoding="utf-8")
            return ast.parse(content, filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            logger.debug(f"Failed to parse {path}: {e}")
            return None

    def _analyze_naming_conventions(self) -> CodePattern | None:
        """
        Analyze naming conventions in code.

        Checks:
        - Function names (snake_case vs camelCase)
        - Variable names
        - Class names (PascalCase)
        """
        function_names: list[str] = []
        class_names: list[str] = []
        variable_names: list[str] = []

        for path in self._analyzed_files:
            tree = self._parse_file(path)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    function_names.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    class_names.append(node.name)
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        variable_names.append(node.id)

        if not function_names:
            return None

        # Check naming patterns
        snake_count = sum(1 for n in function_names if self._is_snake_case(n))
        camel_count = sum(1 for n in function_names if self._is_camel_case(n))
        total = len(function_names)

        snake_ratio = snake_count / total if total else 0
        camel_ratio = camel_count / total if total else 0

        # Check private naming
        private_count = sum(1 for n in function_names if n.startswith("_"))
        private_ratio = private_count / total if total else 0

        # Check dunder usage
        dunder_count = sum(1 for n in function_names if n.startswith("__") and n.endswith("__"))
        dunder_ratio = dunder_count / total if total else 0

        details = {
            "snake_case_ratio": snake_ratio,
            "camel_case_ratio": camel_ratio,
            "private_ratio": private_ratio,
            "dunder_ratio": dunder_ratio,
            "total_functions": float(total),
            "total_classes": float(len(class_names)),
        }

        if snake_ratio > 0.8:
            description = f"Strong snake_case convention ({snake_ratio:.0%})"
            confidence = snake_ratio
        elif camel_ratio > 0.5:
            description = f"Mixed/camelCase naming ({camel_ratio:.0%})"
            confidence = camel_ratio
        else:
            description = "Mixed naming conventions"
            confidence = 0.5

        # Sample evidence
        evidence = tuple(function_names[:10])

        return CodePattern(
            pattern_type="naming",
            description=description,
            confidence=confidence,
            evidence=evidence,
            details=details,
        )

    def _analyze_type_hints(self) -> CodePattern | None:
        """
        Analyze type hint usage.

        Checks:
        - Function argument annotations
        - Return type annotations
        - Variable annotations
        """
        total_functions = 0
        annotated_args = 0
        total_args = 0
        annotated_returns = 0

        for path in self._analyzed_files:
            tree = self._parse_file(path)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    total_functions += 1

                    # Check arguments
                    for arg in node.args.args:
                        total_args += 1
                        if arg.annotation is not None:
                            annotated_args += 1

                    # Check return annotation
                    if node.returns is not None:
                        annotated_returns += 1

        if total_functions < 10:
            return None

        arg_annotation_ratio = annotated_args / total_args if total_args else 0
        return_annotation_ratio = annotated_returns / total_functions if total_functions else 0
        overall_ratio = (arg_annotation_ratio + return_annotation_ratio) / 2

        details = {
            "arg_annotation_ratio": arg_annotation_ratio,
            "return_annotation_ratio": return_annotation_ratio,
            "total_functions": float(total_functions),
            "total_args": float(total_args),
        }

        if overall_ratio > 0.7:
            description = f"Strong type hint usage ({overall_ratio:.0%})"
            confidence = overall_ratio
        elif overall_ratio > 0.3:
            description = f"Partial type hint usage ({overall_ratio:.0%})"
            confidence = 0.6
        else:
            description = f"Limited type hints ({overall_ratio:.0%})"
            confidence = 0.5

        return CodePattern(
            pattern_type="typing",
            description=description,
            confidence=confidence,
            evidence=(
                f"Annotated args: {annotated_args}/{total_args}",
                f"Annotated returns: {annotated_returns}/{total_functions}",
            ),
            details=details,
        )

    def _analyze_docstrings(self) -> CodePattern | None:
        """
        Analyze docstring usage and style.

        Checks:
        - Module docstrings
        - Class docstrings
        - Function docstrings
        - Docstring style (Google, numpy, etc.)
        """
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        total_modules = 0
        documented_modules = 0

        docstring_samples: list[str] = []

        for path in self._analyzed_files:
            tree = self._parse_file(path)
            if tree is None:
                continue

            total_modules += 1

            # Module docstring
            if ast.get_docstring(tree):
                documented_modules += 1
                doc = ast.get_docstring(tree) or ""
                if doc and len(docstring_samples) < 5:
                    docstring_samples.append(doc[:100])

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    total_functions += 1
                    if ast.get_docstring(node):
                        documented_functions += 1
                        doc = ast.get_docstring(node) or ""
                        if doc and len(docstring_samples) < 5:
                            docstring_samples.append(doc[:100])

                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                    if ast.get_docstring(node):
                        documented_classes += 1

        if total_functions < 10:
            return None

        func_ratio = documented_functions / total_functions if total_functions else 0
        class_ratio = documented_classes / total_classes if total_classes else 0
        module_ratio = documented_modules / total_modules if total_modules else 0

        overall_ratio = (
            (func_ratio + class_ratio + module_ratio) / 3
            if total_classes
            else (func_ratio + module_ratio) / 2
        )

        details = {
            "function_docstring_ratio": func_ratio,
            "class_docstring_ratio": class_ratio,
            "module_docstring_ratio": module_ratio,
            "total_functions": float(total_functions),
            "total_classes": float(total_classes),
        }

        if overall_ratio > 0.7:
            description = f"Well documented codebase ({overall_ratio:.0%})"
            confidence = overall_ratio
        elif overall_ratio > 0.3:
            description = f"Partially documented ({overall_ratio:.0%})"
            confidence = 0.6
        else:
            description = f"Limited documentation ({overall_ratio:.0%})"
            confidence = 0.5

        return CodePattern(
            pattern_type="docstrings",
            description=description,
            confidence=confidence,
            evidence=tuple(docstring_samples[:3]),
            details=details,
        )

    def _analyze_structure(self) -> CodePattern | None:
        """
        Analyze code structure (class vs function heavy).

        Checks:
        - Class to function ratio
        - Average methods per class
        - Inheritance patterns
        """
        total_classes = 0
        total_functions = 0  # Module-level only
        methods_per_class: list[int] = []
        classes_with_inheritance = 0

        for path in self._analyzed_files:
            tree = self._parse_file(path)
            if tree is None:
                continue

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    total_classes += 1

                    # Count methods
                    methods = sum(
                        1
                        for child in node.body
                        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef)
                    )
                    methods_per_class.append(methods)

                    # Check inheritance
                    if node.bases:
                        classes_with_inheritance += 1

                elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    total_functions += 1

        if total_classes + total_functions < 10:
            return None

        avg_methods = sum(methods_per_class) / len(methods_per_class) if methods_per_class else 0
        inheritance_ratio = classes_with_inheritance / total_classes if total_classes else 0

        # Determine structure style
        total_items = total_classes + total_functions
        class_ratio = total_classes / total_items if total_items else 0

        details = {
            "class_ratio": class_ratio,
            "avg_methods_per_class": avg_methods,
            "inheritance_ratio": inheritance_ratio,
            "total_classes": float(total_classes),
            "total_functions": float(total_functions),
        }

        if class_ratio > 0.5:
            description = (
                f"Class-heavy structure ({class_ratio:.0%} classes, avg {avg_methods:.1f} methods)"
            )
            confidence = class_ratio
        elif class_ratio < 0.2:
            description = f"Function-heavy structure ({total_functions} functions)"
            confidence = 1 - class_ratio
        else:
            description = (
                f"Balanced structure ({total_classes} classes, {total_functions} functions)"
            )
            confidence = 0.5

        return CodePattern(
            pattern_type="structure",
            description=description,
            confidence=confidence,
            evidence=(
                f"Classes: {total_classes}",
                f"Functions: {total_functions}",
                f"Avg methods/class: {avg_methods:.1f}",
                f"Using inheritance: {classes_with_inheritance}/{total_classes}",
            ),
            details=details,
        )

    def _analyze_imports(self) -> CodePattern | None:
        """
        Analyze import patterns.

        Checks:
        - Import organization (standard, third-party, local)
        - Import style (import x vs from x import y)
        - Common dependencies
        """
        import_statements = 0
        from_imports = 0
        absolute_imports = 0
        relative_imports = 0
        imported_modules: Counter[str] = Counter()

        for path in self._analyzed_files:
            tree = self._parse_file(path)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    import_statements += 1
                    for alias in node.names:
                        module = alias.name.split(".")[0]
                        imported_modules[module] += 1

                elif isinstance(node, ast.ImportFrom):
                    from_imports += 1
                    if node.level > 0:
                        relative_imports += 1
                    else:
                        absolute_imports += 1

                    if node.module:
                        module = node.module.split(".")[0]
                        imported_modules[module] += 1

        total_imports = import_statements + from_imports
        if total_imports < 20:
            return None

        from_ratio = from_imports / total_imports if total_imports else 0
        relative_ratio = relative_imports / from_imports if from_imports else 0

        top_modules = imported_modules.most_common(10)

        details = {
            "from_import_ratio": from_ratio,
            "relative_import_ratio": relative_ratio,
            "total_imports": float(total_imports),
            "unique_modules": float(len(imported_modules)),
        }

        if from_ratio > 0.7:
            description = f"Prefers 'from' imports ({from_ratio:.0%})"
            confidence = from_ratio
        elif from_ratio < 0.3:
            description = f"Prefers 'import' statements ({1 - from_ratio:.0%})"
            confidence = 1 - from_ratio
        else:
            description = "Mixed import style"
            confidence = 0.5

        if relative_ratio > 0.3:
            description += f", uses relative imports ({relative_ratio:.0%})"

        return CodePattern(
            pattern_type="imports",
            description=description,
            confidence=confidence,
            evidence=tuple(f"{m}: {c}" for m, c in top_modules[:5]),
            details=details,
        )

    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        if name.startswith("_"):
            name = name.lstrip("_")
        return bool(re.match(r"^[a-z][a-z0-9_]*$", name))

    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase convention."""
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", name)) and "_" not in name


def analyze_code(
    repo_path: Path | str,
    sample_size: int = 50,
) -> list[CodePattern]:
    """
    Convenience function to analyze code patterns.

    Args:
        repo_path: Path to the repository
        sample_size: Maximum number of files to analyze

    Returns:
        List of detected patterns
    """
    analyzer = CodePatternAnalyzer(
        repo_path=Path(repo_path),
        sample_size=sample_size,
    )
    return analyzer.analyze()


__all__ = [
    "CodePattern",
    "CodePatternAnalyzer",
    "CodeAnalyzerError",
    "analyze_code",
]
