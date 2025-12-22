"""
File Lens System for Context Perception.

Large files are virtualized through semantic lenses. Instead of showing
"monolith.py:847-920", the agent sees "auth_core:validate_token".

Spec: spec/protocols/context-perception.md §8

A FileLens is a bidirectional view:
    get: Extract the focused slice from the whole
    put: Write changes back from the slice to the whole

Teaching:
    gotcha: Lenses are bidirectional. If you edit the focused slice,
            put() will update the original file correctly.
            (Evidence: test_lens.py::test_lens_bidirectionality)

    gotcha: visible_name is semantic, not positional. "validate_token"
            not "lines 847-920". This helps agents reason about code.
            (Evidence: test_lens.py::test_semantic_naming)
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

# === Focus Types ===


class FocusType(Enum):
    """Types of focus specifications."""

    FUNCTION = auto()  # Focus on a function
    CLASS = auto()  # Focus on a class
    METHOD = auto()  # Focus on a method within a class
    RANGE = auto()  # Focus on a line range
    PATTERN = auto()  # Focus on lines matching a pattern


@dataclass
class FocusSpec:
    """
    Specification for what to focus on in a file.

    This is the "selector" for creating a lens.
    """

    focus_type: FocusType
    name: str | None = None  # Function/class/method name
    class_name: str | None = None  # For methods: the containing class
    start_line: int | None = None  # For ranges
    end_line: int | None = None  # For ranges
    pattern: str | None = None  # For pattern matching

    @classmethod
    def function(cls, name: str) -> "FocusSpec":
        """Focus on a function by name."""
        return cls(focus_type=FocusType.FUNCTION, name=name)

    @classmethod
    def class_(cls, name: str) -> "FocusSpec":
        """Focus on a class by name."""
        return cls(focus_type=FocusType.CLASS, name=name)

    @classmethod
    def method(cls, class_name: str, method_name: str) -> "FocusSpec":
        """Focus on a method within a class."""
        return cls(
            focus_type=FocusType.METHOD,
            name=method_name,
            class_name=class_name,
        )

    @classmethod
    def range(cls, start: int, end: int) -> "FocusSpec":
        """Focus on a line range (1-indexed, inclusive)."""
        return cls(
            focus_type=FocusType.RANGE,
            start_line=start,
            end_line=end,
        )

    @classmethod
    def matching(cls, pattern: str) -> "FocusSpec":
        """Focus on lines matching a regex pattern."""
        return cls(focus_type=FocusType.PATTERN, pattern=pattern)


# === File Lens ===


@dataclass
class FileLens:
    """
    A bidirectional view into a file (§8.2).

    The lens extracts a focused slice from a file and can write
    changes back. The agent sees semantic names, not line numbers.

    Teaching:
        gotcha: FileLens is immutable. get() and put() return new values,
                they don't modify the lens or the original file.
                (Evidence: test_lens.py::test_lens_immutability)

        gotcha: The visible_name should be semantically meaningful.
                "auth_core:validate_token" not "monolith.py:847-920".
                (Evidence: test_lens.py::test_semantic_naming)
    """

    source_path: str  # Path to the source file
    focus: FocusSpec  # What to focus on

    # Resolved positions (computed after creation)
    visible_name: str = ""  # Semantic name (e.g., "auth_core:validate_token")
    visible_content: str = ""  # The focused slice
    line_range: tuple[int, int] = (0, 0)  # (start, end) 1-indexed, inclusive

    # Original content for put() operations
    _original_content: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        # If content not provided, try to load and resolve
        if not self.visible_content and self.source_path:
            path = Path(self.source_path)
            if path.exists():
                self._original_content = path.read_text()
                self._resolve()

    def _resolve(self) -> None:
        """Resolve the focus spec to actual content."""
        if not self._original_content:
            return

        lines = self._original_content.split("\n")

        match self.focus.focus_type:
            case FocusType.FUNCTION:
                self._resolve_function(lines)
            case FocusType.CLASS:
                self._resolve_class(lines)
            case FocusType.METHOD:
                self._resolve_method(lines)
            case FocusType.RANGE:
                self._resolve_range(lines)
            case FocusType.PATTERN:
                self._resolve_pattern(lines)

    def _resolve_function(self, lines: list[str]) -> None:
        """Resolve a function focus."""
        try:
            tree = ast.parse(self._original_content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.focus.name:
                start = node.lineno
                end = node.end_lineno or start

                self.line_range = (start, end)
                self.visible_content = "\n".join(lines[start - 1 : end])

                # Create semantic name
                module_name = Path(self.source_path).stem
                self.visible_name = f"{module_name}:{node.name}"
                return

    def _resolve_class(self, lines: list[str]) -> None:
        """Resolve a class focus."""
        try:
            tree = ast.parse(self._original_content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == self.focus.name:
                start = node.lineno
                end = node.end_lineno or start

                self.line_range = (start, end)
                self.visible_content = "\n".join(lines[start - 1 : end])

                # Create semantic name
                module_name = Path(self.source_path).stem
                self.visible_name = f"{module_name}:{node.name}"
                return

    def _resolve_method(self, lines: list[str]) -> None:
        """Resolve a method within a class."""
        try:
            tree = ast.parse(self._original_content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == self.focus.class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == self.focus.name:
                        start = item.lineno
                        end = item.end_lineno or start

                        self.line_range = (start, end)
                        self.visible_content = "\n".join(lines[start - 1 : end])

                        # Create semantic name
                        module_name = Path(self.source_path).stem
                        self.visible_name = f"{module_name}:{node.name}.{item.name}"
                        return

    def _resolve_range(self, lines: list[str]) -> None:
        """Resolve a line range."""
        start = max(1, self.focus.start_line or 1)
        end = min(len(lines), self.focus.end_line or len(lines))

        self.line_range = (start, end)
        self.visible_content = "\n".join(lines[start - 1 : end])

        # Create semantic name
        module_name = Path(self.source_path).stem
        self.visible_name = f"{module_name}:L{start}-{end}"

    def _resolve_pattern(self, lines: list[str]) -> None:
        """Resolve lines matching a pattern."""
        if not self.focus.pattern:
            return

        try:
            pattern = re.compile(self.focus.pattern)
        except re.error:
            return

        matching_lines: list[tuple[int, str]] = []
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                matching_lines.append((i, line))

        if not matching_lines:
            return

        start = matching_lines[0][0]
        end = matching_lines[-1][0]

        self.line_range = (start, end)
        self.visible_content = "\n".join(line for _, line in matching_lines)

        # Create semantic name
        module_name = Path(self.source_path).stem
        self.visible_name = f"{module_name}:/{self.focus.pattern}/"

    def get(self, whole: str | None = None) -> str:
        """
        Extract the focused slice from the whole file.

        If whole is not provided, uses the original content.
        """
        if whole is None:
            return self.visible_content

        lines = whole.split("\n")
        start, end = self.line_range
        if start == 0 or end == 0:
            return ""

        return "\n".join(lines[start - 1 : end])

    def put(self, part: str, whole: str | None = None) -> str:
        """
        Update the whole file from the modified slice.

        Returns the updated whole content.

        Teaching:
            gotcha: put() replaces the focused range with the new content.
                    The new content may have different line count than original.
                    (Evidence: test_lens.py::test_put_handles_length_change)
        """
        if whole is None:
            whole = self._original_content

        if not whole:
            return part

        lines = whole.split("\n")
        start, end = self.line_range

        if start == 0 or end == 0:
            return whole

        # Split the new content into lines
        new_lines = part.split("\n")

        # Replace the focused range
        result_lines = lines[: start - 1] + new_lines + lines[end:]

        return "\n".join(result_lines)

    def with_content(self, content: str) -> "FileLens":
        """Create a new lens with updated visible content."""
        return FileLens(
            source_path=self.source_path,
            focus=self.focus,
            visible_name=self.visible_name,
            visible_content=content,
            line_range=self.line_range,
            _original_content=self._original_content,
        )


# === Factory Functions ===


def create_lens_for_function(file_path: str, function_name: str) -> FileLens:
    """
    Create a lens focused on a specific function.

    The agent sees "module:function_name" not "file.py:lines 42-78".
    """
    focus = FocusSpec.function(function_name)
    return FileLens(source_path=file_path, focus=focus)


def create_lens_for_class(file_path: str, class_name: str) -> FileLens:
    """Create a lens focused on a specific class."""
    focus = FocusSpec.class_(class_name)
    return FileLens(source_path=file_path, focus=focus)


def create_lens_for_method(
    file_path: str,
    class_name: str,
    method_name: str,
) -> FileLens:
    """Create a lens focused on a specific method within a class."""
    focus = FocusSpec.method(class_name, method_name)
    return FileLens(source_path=file_path, focus=focus)


def create_lens_for_range(
    file_path: str,
    start_line: int,
    end_line: int,
) -> FileLens:
    """Create a lens focused on a line range."""
    focus = FocusSpec.range(start_line, end_line)
    return FileLens(source_path=file_path, focus=focus)


def create_lens_for_pattern(file_path: str, pattern: str) -> FileLens:
    """Create a lens focused on lines matching a pattern."""
    focus = FocusSpec.matching(pattern)
    return FileLens(source_path=file_path, focus=focus)


# === Lens Composition ===


def compose_lenses(outer: FileLens, inner: FileLens) -> FileLens | None:
    """
    Compose two lenses.

    The inner lens operates on the content of the outer lens.
    Returns None if composition is not possible.

    Teaching:
        gotcha: Lens composition requires the inner lens to be defined
                relative to the outer lens's content, not the original file.
                (Evidence: test_lens.py::test_lens_composition)
    """
    if not outer.visible_content:
        return None

    # Create the inner lens on the outer's content
    inner_focus = inner.focus

    # For ranges, we need to adjust
    if inner_focus.focus_type == FocusType.RANGE:
        # The inner range is relative to the outer's content
        inner_lens = FileLens(
            source_path=outer.source_path,
            focus=inner_focus,
            visible_name=f"{outer.visible_name}→{inner.visible_name}",
            visible_content="",
            line_range=(0, 0),
            _original_content=outer.visible_content,
        )
        inner_lens._resolve()
        return inner_lens

    # For other types, create a fresh lens on the outer's content
    # This is a simplified composition
    return None


# === Sane Name Generation ===


def generate_sane_name(
    file_path: str,
    line_range: tuple[int, int],
    ast_node: Any = None,
) -> str:
    """
    Generate a semantically meaningful name for a code region.

    Prefers:
    1. AST-derived names (function/class/method)
    2. Comment-derived names (docstrings, leading comments)
    3. Fallback to line range
    """
    module_name = Path(file_path).stem

    # If we have an AST node, use its name
    if ast_node is not None:
        if hasattr(ast_node, "name"):
            return f"{module_name}:{ast_node.name}"

    # Fallback to line range
    start, end = line_range
    return f"{module_name}:L{start}-{end}"


__all__ = [
    # Types
    "FocusType",
    "FocusSpec",
    "FileLens",
    # Factory functions
    "create_lens_for_function",
    "create_lens_for_class",
    "create_lens_for_method",
    "create_lens_for_range",
    "create_lens_for_pattern",
    # Composition
    "compose_lenses",
    # Utilities
    "generate_sane_name",
]
