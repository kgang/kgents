"""
Docstring Extractor: Source -> DocNode

Parses Python source files and extracts structured documentation:
- Signatures from AST
- Summaries from first docstring line
- Teaching moments from 'Teaching:' sections
- Examples from '>>>' and 'Example:' sections

Teaching:
    gotcha: AST parsing requires valid Python syntax.
            (Evidence: test_extractor.py::test_invalid_syntax)

    gotcha: Teaching section must use 'gotcha:' keyword for extraction.
            (Evidence: test_extractor.py::test_teaching_pattern)
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path
from typing import Iterator

from .types import DocNode, TeachingMoment, Tier


class DocstringExtractor:
    """
    Extract DocNodes from Python source files.

    The extractor handles:
    - Function and class definitions
    - Docstring sections (Teaching:, Example:)
    - Tier determination based on symbol visibility

    Teaching:
        gotcha: Tier determination now includes agents/ and protocols/ as RICH.
                (Evidence: test_extractor.py::test_tier_rich_expanded)
    """

    # Pattern to match teaching moments in docstrings
    # Matches: gotcha: insight text (Evidence: test_path)
    # Note: The insight can span multiple lines with indentation. The regex
    # captures everything up to (Evidence:...) or the next gotcha/end.
    TEACHING_PATTERN = re.compile(
        r"gotcha:\s*"  # Start with gotcha:
        r"(.*?)"  # Capture insight (non-greedy, across lines)
        r"(?:\(Evidence:\s*([^)]+)\))?"  # Optional evidence in parens
        r"(?=\n\s*(?:gotcha:|AGENTESE:|See:|$)|\Z)",  # Stop at next gotcha, AGENTESE, See, empty line, or end
        re.IGNORECASE | re.DOTALL,
    )

    # Pattern to match AGENTESE path declarations
    # Matches: AGENTESE: self.memory.capture
    AGENTESE_PATTERN = re.compile(r"AGENTESE:\s*([\w.]+)", re.IGNORECASE)

    # Pattern to match doctest examples
    EXAMPLE_PATTERN = re.compile(r">>>\s*(.+)")

    # Pattern to match Example: sections
    EXAMPLE_SECTION_PATTERN = re.compile(
        r"Example(?:s)?:\s*\n((?:.*\n)*?)(?=\n\s*(?:[A-Z][a-z]+:|$)|\Z)",
        re.IGNORECASE,
    )

    # Paths to exclude from extraction
    EXCLUDE_PATTERNS: tuple[str, ...] = (
        "node_modules",
        "__pycache__",
        ".pyc",
        "dist/",
        "build/",
        ".git/",
        ".venv/",
        "venv/",
        "_tests/",  # Exclude test directories
        "conftest.py",  # Exclude pytest fixtures
    )

    # Patterns that indicate RICH tier (core implementation paths)
    RICH_PATTERNS: tuple[str, ...] = (
        "services/",
        "services.",
        "agents/",
        "agents.",
        "protocols/",
        "protocols.",
    )

    def should_extract(self, path: Path) -> bool:
        """Check if a file should be extracted (not excluded)."""
        path_str = str(path)
        return not any(p in path_str for p in self.EXCLUDE_PATTERNS)

    def extract_file(self, path: Path) -> list[DocNode]:
        """
        Extract DocNodes from a Python source file.

        Args:
            path: Path to Python file

        Returns:
            List of DocNodes for all documented symbols

        Raises:
            SyntaxError: If file contains invalid Python
            FileNotFoundError: If file doesn't exist
        """
        if not self.should_extract(path):
            return []

        source = path.read_text()
        module_name = self._path_to_module(path)
        return self.extract_module(source, module_name)

    def extract_module_docstring(self, path: Path) -> DocNode | None:
        """
        Extract module-level docstring as a DocNode.

        This captures the file-level documentation including Teaching: sections.
        """
        if not self.should_extract(path):
            return None

        try:
            source = path.read_text()
            tree = ast.parse(source)
            docstring = ast.get_docstring(tree)

            if not docstring:
                return None

            module_name = self._path_to_module(path)
            summary, examples, teaching, agentese_path = self._parse_docstring(docstring)

            return DocNode(
                symbol=path.stem,
                signature=f"module {path.stem}",
                summary=summary,
                examples=examples,
                teaching=teaching,
                tier=Tier.RICH,
                module=module_name,
                agentese_path=agentese_path,
            )
        except SyntaxError:
            return None

    def extract_module(self, source: str, module_name: str = "") -> list[DocNode]:
        """
        Extract DocNodes from Python source code.

        Args:
            source: Python source code
            module_name: Module path (e.g., "services.brain.persistence")

        Returns:
            List of DocNodes
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Return empty list for invalid Python
            return []

        nodes: list[DocNode] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc_node = self._extract_node(node, module_name, source)
                if doc_node is not None:
                    nodes.append(doc_node)

        return nodes

    def _extract_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        module_name: str,
        source: str,
    ) -> DocNode | None:
        """Extract a DocNode from an AST node."""
        docstring = ast.get_docstring(node)

        # Skip nodes without docstrings for non-MINIMAL tiers
        tier = self._determine_tier(node.name, module_name)

        if tier == Tier.MINIMAL:
            # Even MINIMAL needs the signature
            signature = self._extract_signature(node, source)
            return DocNode(
                symbol=node.name,
                signature=signature,
                summary="",
                tier=tier,
                module=module_name,
            )

        if docstring is None:
            return None

        # Parse docstring components
        summary, examples, teaching, agentese_path = self._parse_docstring(docstring)
        signature = self._extract_signature(node, source)

        return DocNode(
            symbol=node.name,
            signature=signature,
            summary=summary,
            examples=examples,
            teaching=teaching,
            tier=tier,
            module=module_name,
            agentese_path=agentese_path,
        )

    def _parse_docstring(
        self, docstring: str
    ) -> tuple[str, tuple[str, ...], tuple[TeachingMoment, ...], str | None]:
        """
        Parse a docstring into components.

        Returns:
            Tuple of (summary, examples, teaching_moments, agentese_path)
        """
        # Summary is the first non-empty line
        lines = docstring.strip().split("\n")
        summary = lines[0].strip() if lines else ""

        # Extract examples from doctest markers
        examples: list[str] = []
        for match in self.EXAMPLE_PATTERN.finditer(docstring):
            examples.append(match.group(1).strip())

        # Also extract from Example: sections
        for section_match in self.EXAMPLE_SECTION_PATTERN.finditer(docstring):
            section_content = section_match.group(1)
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith(">>>"):
                    examples.append(line[3:].strip())
                elif line and not line.startswith("#"):
                    # Include non-doctest example lines
                    examples.append(line)

        # Extract teaching moments
        teaching: list[TeachingMoment] = []
        for match in self.TEACHING_PATTERN.finditer(docstring):
            insight = match.group(1).strip()
            # Clean up multi-line insights
            insight = " ".join(insight.split())
            evidence = match.group(2).strip() if match.group(2) else None

            # Determine severity from keywords
            severity: str = "info"
            insight_lower = insight.lower()
            if any(w in insight_lower for w in ["critical", "must", "never", "always"]):
                severity = "critical"
            elif any(w in insight_lower for w in ["warning", "careful", "note"]):
                severity = "warning"

            teaching.append(
                TeachingMoment(
                    insight=insight,
                    severity=severity,  # type: ignore[arg-type]
                    evidence=evidence,
                )
            )

        # Extract AGENTESE path
        agentese_path: str | None = None
        agentese_match = self.AGENTESE_PATTERN.search(docstring)
        if agentese_match:
            agentese_path = agentese_match.group(1)

        return summary, tuple(examples), tuple(teaching), agentese_path

    def _determine_tier(self, symbol: str, module: str) -> Tier:
        """
        Determine extraction tier based on symbol and module.

        Tier rules:
        - Private (starts with _): MINIMAL
        - Core paths (services/, agents/, protocols/): RICH
        - Everything else: STANDARD
        """
        if symbol.startswith("_") and not symbol.startswith("__"):
            return Tier.MINIMAL

        # Check if module is in a core path that deserves RICH tier
        if any(p in module for p in self.RICH_PATTERNS):
            return Tier.RICH

        return Tier.STANDARD

    def _extract_signature(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        source: str,
    ) -> str:
        """
        Extract the signature of a function or class.

        For functions: includes parameters and return annotation
        For classes: includes base classes
        """
        if isinstance(node, ast.ClassDef):
            bases = ", ".join(ast.unparse(base) for base in node.bases)
            if bases:
                return f"class {node.name}({bases})"
            return f"class {node.name}"

        # Function signature
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        args = ast.unparse(node.args) if node.args else ""
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""

        return f"{prefix} {node.name}({args}){returns}"

    def _path_to_module(self, path: Path) -> str:
        """
        Convert a file path to a module name.

        Example: /path/to/services/brain/persistence.py -> services.brain.persistence
        """
        # Try to find 'impl/claude' as the base
        parts = path.parts
        try:
            impl_idx = parts.index("impl")
            if impl_idx + 1 < len(parts) and parts[impl_idx + 1] == "claude":
                # Start from after impl/claude
                module_parts_tuple = parts[impl_idx + 2 :]
            else:
                module_parts_tuple = parts[-3:]  # Fallback
        except ValueError:
            module_parts_tuple = parts[-3:]  # Fallback

        # Remove .py extension from last part
        module_parts = list(module_parts_tuple)
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)


def extract_from_object(obj: object) -> DocNode | None:
    """
    Extract a DocNode from a Python object.

    Useful for runtime documentation extraction.
    """
    if not hasattr(obj, "__name__"):
        return None

    name = getattr(obj, "__name__", "unknown")
    docstring = inspect.getdoc(obj) or ""
    module = getattr(obj, "__module__", "")

    try:
        if callable(obj):
            signature = str(inspect.signature(obj))
        else:
            signature = "()"
    except (ValueError, TypeError):
        signature = "()"

    # Use a temporary extractor for parsing
    extractor = DocstringExtractor()
    summary, examples, teaching, agentese_path = extractor._parse_docstring(docstring)
    tier = extractor._determine_tier(name, module)

    return DocNode(
        symbol=name,
        signature=f"def {name}{signature}",
        summary=summary,
        examples=examples,
        teaching=teaching,
        tier=tier,
        module=module,
        agentese_path=agentese_path,
    )
