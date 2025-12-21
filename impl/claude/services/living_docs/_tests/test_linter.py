"""
Tests for DocstringLinter.

Type II: Property-based tests for linting logic.

Teaching:
    gotcha: Test both positive (violations) and negative (valid code) cases.
            Linters that only catch errors miss false positives.
            (Evidence: test_linter.py::test_no_false_positives_on_valid_code)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from services.living_docs.linter import (
    DocstringLinter,
    LintResult,
    LintStats,
    lint_directory,
    lint_file,
)


class TestDocstringLinter:
    """Tests for DocstringLinter."""

    @pytest.fixture
    def linter(self) -> DocstringLinter:
        return DocstringLinter()

    # === Rule 1: missing_docstring ===

    def test_missing_docstring_function(self, linter: DocstringLinter) -> None:
        """Public function without docstring is an error."""
        source = textwrap.dedent("""
            def public_function():
                pass
        """)
        results = linter.lint_source(source, "services.test")
        assert len(results) == 1
        assert results[0].issue == "missing_docstring"
        assert results[0].severity == "error"
        assert results[0].symbol == "public_function"

    def test_missing_docstring_class(self, linter: DocstringLinter) -> None:
        """Public class without docstring is an error."""
        source = textwrap.dedent("""
            class PublicClass:
                pass
        """)
        results = linter.lint_source(source, "services.test")
        assert len(results) == 1
        assert results[0].issue == "missing_docstring"
        assert results[0].severity == "error"

    def test_skip_private_symbols(self, linter: DocstringLinter) -> None:
        """Private symbols (with _ prefix) are not linted."""
        source = textwrap.dedent("""
            def _private_function():
                pass

            class _PrivateClass:
                pass
        """)
        results = linter.lint_source(source, "services.test")
        assert len(results) == 0

    def test_lint_dunder_methods(self, linter: DocstringLinter) -> None:
        """Dunder methods like __repr__ should be linted."""
        source = textwrap.dedent("""
            class MyClass:
                '''A class.'''

                def __repr__(self):
                    return 'MyClass'

                def __str__(self):
                    return 'MyClass'
        """)
        results = linter.lint_source(source, "services.test")
        # __repr__ and __str__ are dunder but not exempt (missing docstrings)
        # The class may get missing_teaching warning (RICH tier)
        missing_docstring_results = [r for r in results if r.issue == "missing_docstring"]
        assert len(missing_docstring_results) >= 2
        for r in missing_docstring_results:
            assert r.symbol in ("__repr__", "__str__")

    def test_exempt_all_symbol(self, linter: DocstringLinter) -> None:
        """__all__ is exempt from docstring requirements."""
        source = textwrap.dedent("""
            __all__ = ['foo', 'bar']
        """)
        results = linter.lint_source(source, "test")
        # __all__ is not a function/class, so no results anyway
        assert len(results) == 0

    def test_init_always_exempt(self, linter: DocstringLinter) -> None:
        """__init__ is always exempt (constructors are often trivial)."""
        source = textwrap.dedent("""
            class MyClass:
                '''A class.'''

                def __init__(self, x: int):
                    self.x = x
        """)
        results = linter.lint_source(source, "utils.test")
        # __init__ is exempt, no missing_docstring error for it
        missing_docstring = [r for r in results if r.issue == "missing_docstring"]
        assert len(missing_docstring) == 0

    # === Rule 2: missing_summary ===

    def test_missing_summary_empty(self, linter: DocstringLinter) -> None:
        """Empty docstring (just quotes) is an error."""
        source = textwrap.dedent('''
            def empty_docs():
                """   """
                pass
        ''')
        results = linter.lint_source(source, "services.test")
        assert len(results) == 1
        assert results[0].issue == "missing_summary"
        assert results[0].severity == "error"

    def test_missing_summary_whitespace_only(self, linter: DocstringLinter) -> None:
        """Whitespace-only docstring is an error."""
        source = textwrap.dedent('''
            def whitespace_docs():
                """

                """
                pass
        ''')
        results = linter.lint_source(source, "services.test")
        assert len(results) == 1
        assert results[0].issue == "missing_summary"

    def test_valid_summary(self, linter: DocstringLinter) -> None:
        """Valid docstring with summary passes."""
        source = textwrap.dedent('''
            def valid_docs():
                """This is a valid summary."""
                pass
        ''')
        results = linter.lint_source(source, "services.test")
        assert len(results) == 0

    # === Rule 3: missing_teaching ===

    def test_missing_teaching_rich_class(self, linter: DocstringLinter) -> None:
        """RICH tier class without Teaching section is a warning."""
        source = textwrap.dedent('''
            class ImportantService:
                """An important service without teaching moments."""
                pass
        ''')
        results = linter.lint_source(source, "services.brain.core")
        # Should have a warning for missing teaching
        teaching_issues = [r for r in results if r.issue == "missing_teaching"]
        assert len(teaching_issues) == 1
        assert teaching_issues[0].severity == "warning"

    def test_teaching_present_no_warning(self, linter: DocstringLinter) -> None:
        """RICH tier class with Teaching section passes."""
        source = textwrap.dedent('''
            class WellDocumented:
                """A well-documented class.

                Teaching:
                    gotcha: Always remember this.
                """
                pass
        ''')
        results = linter.lint_source(source, "services.brain.core")
        teaching_issues = [r for r in results if r.issue == "missing_teaching"]
        assert len(teaching_issues) == 0

    def test_teaching_not_required_for_functions(self, linter: DocstringLinter) -> None:
        """Teaching sections are only required for RICH tier classes, not functions."""
        source = textwrap.dedent('''
            def helper_function():
                """A helper function without teaching."""
                pass
        ''')
        results = linter.lint_source(source, "services.brain.core")
        assert len(results) == 0

    def test_teaching_not_required_non_rich(self, linter: DocstringLinter) -> None:
        """Teaching sections are not required for non-RICH tier."""
        source = textwrap.dedent('''
            class UtilClass:
                """A utility class."""
                pass
        ''')
        results = linter.lint_source(source, "utils.helpers")
        assert len(results) == 0

    # === Edge Cases ===

    def test_invalid_syntax_graceful(self, linter: DocstringLinter) -> None:
        """Invalid Python syntax returns empty results, not exception."""
        source = "def broken("
        results = linter.lint_source(source, "test")
        assert results == []

    def test_empty_source(self, linter: DocstringLinter) -> None:
        """Empty source returns empty results."""
        results = linter.lint_source("", "test")
        assert results == []

    def test_lint_broken_imports(self, linter: DocstringLinter) -> None:
        """Code with broken imports can still be linted (AST-based)."""
        source = textwrap.dedent('''
            from nonexistent.module import Thing

            def uses_thing():
                """This uses a non-existent import."""
                return Thing()
        ''')
        # Should not crash, should lint the function
        results = linter.lint_source(source, "test")
        # The function has a docstring, so no issues
        assert len(results) == 0

    def test_no_false_positives_on_valid_code(self, linter: DocstringLinter) -> None:
        """Well-documented code produces no lint results."""
        source = textwrap.dedent('''
            """Module docstring."""

            class WellDocumented:
                """A well-documented class.

                Teaching:
                    gotcha: Remember this important thing.
                """

                def method(self):
                    """A documented method."""
                    pass

            def helper(x: int) -> int:
                """A helper function.

                Args:
                    x: Input value

                Returns:
                    Processed value
                """
                return x * 2
        ''')
        results = linter.lint_source(source, "services.test")
        errors = [r for r in results if r.severity == "error"]
        assert len(errors) == 0

    # === Tier Detection ===

    def test_rich_tier_detection_services(self, linter: DocstringLinter) -> None:
        """services.* modules are RICH tier."""
        source = textwrap.dedent('''
            class ServiceClass:
                """A service class."""
                pass
        ''')
        results = linter.lint_source(source, "services.brain.core")
        # RICH tier class should get warning for missing teaching
        assert any(r.issue == "missing_teaching" for r in results)

    def test_rich_tier_detection_agents(self, linter: DocstringLinter) -> None:
        """agents.* modules are RICH tier."""
        source = textwrap.dedent('''
            class AgentClass:
                """An agent class."""
                pass
        ''')
        results = linter.lint_source(source, "agents.poly.core")
        assert any(r.issue == "missing_teaching" for r in results)

    def test_rich_tier_detection_protocols(self, linter: DocstringLinter) -> None:
        """protocols.* modules are RICH tier."""
        source = textwrap.dedent('''
            class ProtocolClass:
                """A protocol class."""
                pass
        ''')
        results = linter.lint_source(source, "protocols.agentese.gateway")
        assert any(r.issue == "missing_teaching" for r in results)


class TestLintResult:
    """Tests for LintResult dataclass."""

    def test_to_dict(self) -> None:
        """LintResult.to_dict produces expected structure."""
        result = LintResult(
            symbol="my_func",
            module="services.test",
            issue="missing_docstring",
            severity="error",
            line=42,
            message="Missing docstring",
        )
        d = result.to_dict()
        assert d["symbol"] == "my_func"
        assert d["module"] == "services.test"
        assert d["issue"] == "missing_docstring"
        assert d["severity"] == "error"
        assert d["line"] == 42


class TestLintStats:
    """Tests for LintStats dataclass."""

    def test_to_dict(self) -> None:
        """LintStats.to_dict produces expected structure."""
        stats = LintStats(
            files_checked=10,
            symbols_checked=50,
            errors=3,
            warnings=5,
            results=[
                LintResult(
                    symbol="foo",
                    module="test",
                    issue="missing_docstring",
                    severity="error",
                    line=1,
                )
            ],
        )
        d = stats.to_dict()
        assert d["files_checked"] == 10
        assert d["symbols_checked"] == 50
        assert d["errors"] == 3
        assert d["warnings"] == 5
        assert len(d["results"]) == 1


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_lint_file_nonexistent(self, tmp_path: Path) -> None:
        """lint_file on non-existent file returns empty list."""
        fake_path = tmp_path / "nonexistent.py"
        results = lint_file(fake_path)
        assert results == []

    def test_lint_file_not_python(self, tmp_path: Path) -> None:
        """lint_file on non-Python file returns empty list."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("Hello world")
        results = lint_file(txt_file)
        assert results == []

    def test_lint_file_valid(self, tmp_path: Path) -> None:
        """lint_file on valid Python file works."""
        py_file = tmp_path / "module.py"
        py_file.write_text("def undocumented():\n    pass\n")
        results = lint_file(py_file)
        assert len(results) == 1
        assert results[0].issue == "missing_docstring"

    def test_lint_directory(self, tmp_path: Path) -> None:
        """lint_directory processes all Python files."""
        (tmp_path / "a.py").write_text("def a():\n    pass\n")
        (tmp_path / "b.py").write_text('def b():\n    """Documented."""\n    pass\n')
        stats = lint_directory(tmp_path)
        assert stats.files_checked == 2
        assert stats.errors == 1  # Only a.py has an error


class TestExcludePatterns:
    """Tests for path exclusion."""

    @pytest.fixture
    def linter(self) -> DocstringLinter:
        return DocstringLinter()

    def test_exclude_tests_directory(self, linter: DocstringLinter) -> None:
        """_tests/ directories are excluded."""
        assert not linter.should_lint(Path("/path/to/_tests/test_foo.py"))

    def test_exclude_conftest(self, linter: DocstringLinter) -> None:
        """conftest.py files are excluded."""
        assert not linter.should_lint(Path("/path/to/conftest.py"))

    def test_exclude_venv(self, linter: DocstringLinter) -> None:
        """Virtual environment directories are excluded."""
        assert not linter.should_lint(Path("/path/to/.venv/lib/foo.py"))
        assert not linter.should_lint(Path("/path/to/venv/lib/foo.py"))

    def test_include_regular_py(self, linter: DocstringLinter) -> None:
        """Regular Python files are included."""
        assert linter.should_lint(Path("/path/to/services/brain/core.py"))


class TestAsyncFunctions:
    """Tests for async function handling."""

    @pytest.fixture
    def linter(self) -> DocstringLinter:
        return DocstringLinter()

    def test_async_function_without_docstring(self, linter: DocstringLinter) -> None:
        """Async functions without docstrings are errors."""
        source = textwrap.dedent("""
            async def fetch_data():
                pass
        """)
        results = linter.lint_source(source, "services.test")
        assert len(results) == 1
        assert results[0].issue == "missing_docstring"
        assert results[0].symbol == "fetch_data"

    def test_async_function_with_docstring(self, linter: DocstringLinter) -> None:
        """Async functions with docstrings pass."""
        source = textwrap.dedent('''
            async def fetch_data():
                """Fetch data from the server."""
                pass
        ''')
        results = linter.lint_source(source, "services.test")
        assert len(results) == 0
