"""
Tests for the File Lens System.

These tests verify semantic file virtualization.

Spec: spec/protocols/context-perception.md §8
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ..lens import (
    FocusType,
    FocusSpec,
    FileLens,
    create_lens_for_function,
    create_lens_for_class,
    create_lens_for_method,
    create_lens_for_range,
    create_lens_for_pattern,
    generate_sane_name,
)


# === FocusSpec Tests ===


class TestFocusSpec:
    """Tests for FocusSpec factory methods."""

    def test_function_focus(self) -> None:
        """Create function focus."""
        spec = FocusSpec.function("validate_token")

        assert spec.focus_type == FocusType.FUNCTION
        assert spec.name == "validate_token"

    def test_class_focus(self) -> None:
        """Create class focus."""
        spec = FocusSpec.class_("AuthMiddleware")

        assert spec.focus_type == FocusType.CLASS
        assert spec.name == "AuthMiddleware"

    def test_method_focus(self) -> None:
        """Create method focus."""
        spec = FocusSpec.method("AuthMiddleware", "validate")

        assert spec.focus_type == FocusType.METHOD
        assert spec.name == "validate"
        assert spec.class_name == "AuthMiddleware"

    def test_range_focus(self) -> None:
        """Create range focus."""
        spec = FocusSpec.range(10, 20)

        assert spec.focus_type == FocusType.RANGE
        assert spec.start_line == 10
        assert spec.end_line == 20

    def test_pattern_focus(self) -> None:
        """Create pattern focus."""
        spec = FocusSpec.matching(r"def test_\w+")

        assert spec.focus_type == FocusType.PATTERN
        assert spec.pattern == r"def test_\w+"


# === FileLens Tests ===


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    content = '''"""Module docstring."""

def helper():
    """A helper function."""
    return 42


class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b


def validate_token(token: str) -> bool:
    """Validate a JWT token."""
    if not token:
        return False
    # Check token format
    parts = token.split(".")
    return len(parts) == 3
'''
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


class TestFileLens:
    """Tests for FileLens bidirectional views."""

    def test_function_lens(self, sample_python_file: Path) -> None:
        """Create lens for a function."""
        lens = create_lens_for_function(str(sample_python_file), "helper")

        assert lens.visible_name == "sample:helper"
        assert "def helper():" in lens.visible_content
        assert "return 42" in lens.visible_content
        assert lens.line_range[0] > 0

    def test_class_lens(self, sample_python_file: Path) -> None:
        """Create lens for a class."""
        lens = create_lens_for_class(str(sample_python_file), "Calculator")

        assert lens.visible_name == "sample:Calculator"
        assert "class Calculator:" in lens.visible_content
        assert "def add" in lens.visible_content
        assert "def subtract" in lens.visible_content

    def test_method_lens(self, sample_python_file: Path) -> None:
        """Create lens for a method."""
        lens = create_lens_for_method(str(sample_python_file), "Calculator", "add")

        assert lens.visible_name == "sample:Calculator.add"
        assert "def add" in lens.visible_content
        assert "return a + b" in lens.visible_content
        # Should NOT include subtract
        assert "def subtract" not in lens.visible_content

    def test_range_lens(self, sample_python_file: Path) -> None:
        """Create lens for a line range."""
        lens = create_lens_for_range(str(sample_python_file), 1, 5)

        assert lens.visible_name == "sample:L1-5"
        assert lens.line_range == (1, 5)

    def test_pattern_lens(self, sample_python_file: Path) -> None:
        """Create lens for pattern matching."""
        lens = create_lens_for_pattern(str(sample_python_file), r"return")

        assert "return" in lens.visible_content

    def test_semantic_naming(self, sample_python_file: Path) -> None:
        """Lens uses semantic names, not line numbers."""
        lens = create_lens_for_function(str(sample_python_file), "validate_token")

        # Semantic name
        assert lens.visible_name == "sample:validate_token"

        # NOT line number based
        assert "L" not in lens.visible_name
        assert "-" not in lens.visible_name or "validate" in lens.visible_name

    def test_get_extracts_slice(self, sample_python_file: Path) -> None:
        """get() extracts the focused slice."""
        lens = create_lens_for_function(str(sample_python_file), "helper")
        whole = sample_python_file.read_text()

        extracted = lens.get(whole)

        assert "def helper():" in extracted
        assert "class Calculator" not in extracted

    def test_put_updates_whole(self, sample_python_file: Path) -> None:
        """put() updates the whole file from modified slice."""
        lens = create_lens_for_function(str(sample_python_file), "helper")
        whole = sample_python_file.read_text()

        # Modify the slice
        new_content = '''def helper():
    """Modified helper."""
    return 100'''

        updated = lens.put(new_content, whole)

        # Original function replaced
        assert "return 100" in updated
        assert "return 42" not in updated

        # Rest of file intact
        assert "class Calculator" in updated
        assert "validate_token" in updated

    def test_put_handles_length_change(self, sample_python_file: Path) -> None:
        """put() handles content with different line count."""
        lens = create_lens_for_function(str(sample_python_file), "helper")
        whole = sample_python_file.read_text()
        original_lines = len(whole.split("\n"))

        # Replace with longer content
        new_content = '''def helper():
    """Much longer helper."""
    x = 1
    y = 2
    z = 3
    return x + y + z'''

        updated = lens.put(new_content, whole)
        new_lines = len(updated.split("\n"))

        # Line count changed but structure intact
        assert new_lines > original_lines
        assert "class Calculator" in updated

    def test_lens_immutability(self, sample_python_file: Path) -> None:
        """Lens operations return new values, don't modify."""
        lens = create_lens_for_function(str(sample_python_file), "helper")
        original_content = lens.visible_content

        # get() doesn't modify
        lens.get()
        assert lens.visible_content == original_content

        # put() doesn't modify lens
        lens.put("new content")
        assert lens.visible_content == original_content

    def test_with_content(self, sample_python_file: Path) -> None:
        """with_content() creates new lens with updated content."""
        lens = create_lens_for_function(str(sample_python_file), "helper")
        original = lens.visible_content

        new_lens = lens.with_content("Modified content")

        # Original unchanged
        assert lens.visible_content == original

        # New lens has new content
        assert new_lens.visible_content == "Modified content"

        # Other attributes preserved
        assert new_lens.source_path == lens.source_path
        assert new_lens.visible_name == lens.visible_name


class TestLensEdgeCases:
    """Tests for edge cases."""

    def test_nonexistent_function(self, sample_python_file: Path) -> None:
        """Lens for nonexistent function."""
        lens = create_lens_for_function(str(sample_python_file), "nonexistent")

        # Should have empty content, not crash
        assert lens.visible_content == ""
        assert lens.line_range == (0, 0)

    def test_nonexistent_file(self) -> None:
        """Lens for nonexistent file."""
        lens = create_lens_for_function("/nonexistent/path.py", "foo")

        assert lens.visible_content == ""

    def test_syntax_error_file(self, tmp_path: Path) -> None:
        """Lens for file with syntax errors."""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n")

        lens = create_lens_for_function(str(bad_file), "broken")

        # Should not crash, just empty
        assert lens.line_range == (0, 0)


class TestGenerateSaneName:
    """Tests for semantic name generation."""

    def test_with_ast_node(self) -> None:
        """Generate name from AST node."""
        import ast

        node = ast.FunctionDef(
            name="validate",
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=[],
            decorator_list=[],
        )

        name = generate_sane_name("/path/to/auth.py", (10, 20), node)

        assert name == "auth:validate"

    def test_fallback_to_range(self) -> None:
        """Fallback to line range when no AST node."""
        name = generate_sane_name("/path/to/module.py", (100, 150))

        assert name == "module:L100-150"


# === Integration Tests ===


class TestLensIntegration:
    """Integration tests for lens workflows."""

    def test_edit_workflow(self, sample_python_file: Path) -> None:
        """Complete edit workflow: focus -> modify -> write back."""
        # 1. Create lens
        lens = create_lens_for_function(str(sample_python_file), "validate_token")

        # 2. Verify we got the right content
        assert "Validate a JWT token" in lens.visible_content

        # 3. Modify
        modified = lens.visible_content.replace(
            "len(parts) == 3",
            "len(parts) >= 3"
        )

        # 4. Write back
        whole = sample_python_file.read_text()
        updated = lens.put(modified, whole)

        # 5. Verify change applied
        assert "len(parts) >= 3" in updated
        assert "len(parts) == 3" not in updated

        # 6. Rest of file intact
        assert "class Calculator" in updated

    def test_multiple_lenses_same_file(self, sample_python_file: Path) -> None:
        """Create multiple lenses into same file."""
        lens1 = create_lens_for_function(str(sample_python_file), "helper")
        lens2 = create_lens_for_class(str(sample_python_file), "Calculator")
        lens3 = create_lens_for_function(str(sample_python_file), "validate_token")

        # Each focuses on different content
        assert "helper" in lens1.visible_name
        assert "Calculator" in lens2.visible_name
        assert "validate_token" in lens3.visible_name

        # Contents don't overlap (except potentially docstrings)
        assert "class Calculator" not in lens1.visible_content
        assert "def helper" not in lens2.visible_content
