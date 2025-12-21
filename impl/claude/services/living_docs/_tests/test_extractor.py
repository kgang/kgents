"""
Tests for DocstringExtractor.

Type II: Property-based tests for extraction logic.

Teaching:
    gotcha: Use textwrap.dedent for multi-line docstring fixtures.
            (Evidence: test_extractor.py::test_teaching_pattern)
"""

from __future__ import annotations

import textwrap

import pytest
from hypothesis import given, settings, strategies as st

from services.living_docs.extractor import DocstringExtractor, extract_from_object
from services.living_docs.types import Tier


class TestDocstringExtractor:
    """Tests for DocstringExtractor."""

    @pytest.fixture
    def extractor(self) -> DocstringExtractor:
        return DocstringExtractor()

    # === Summary Extraction ===

    def test_extract_summary_single_line(self, extractor: DocstringExtractor) -> None:
        """First line becomes summary."""
        source = textwrap.dedent('''
            def foo():
                """This is the summary."""
                pass
        ''')
        nodes = extractor.extract_module(source, "test")
        assert len(nodes) == 1
        assert nodes[0].summary == "This is the summary."

    def test_extract_summary_multiline(self, extractor: DocstringExtractor) -> None:
        """Multi-line docstring: only first line is summary."""
        source = textwrap.dedent('''
            def bar():
                """First line summary.

                More details here.
                """
                pass
        ''')
        nodes = extractor.extract_module(source, "test")
        assert nodes[0].summary == "First line summary."

    # === Teaching Moment Extraction ===

    def test_teaching_pattern_basic(self, extractor: DocstringExtractor) -> None:
        """Basic gotcha extraction without evidence."""
        source = textwrap.dedent('''
            def risky():
                """Do something risky.

                Teaching:
                    gotcha: Always check the return value.
                """
                pass
        ''')
        nodes = extractor.extract_module(source, "services.test")
        assert len(nodes) == 1
        assert len(nodes[0].teaching) == 1
        assert "Always check the return value" in nodes[0].teaching[0].insight

    def test_teaching_pattern_with_evidence(self, extractor: DocstringExtractor) -> None:
        """Gotcha extraction with evidence reference."""
        source = textwrap.dedent('''
            class Dangerous:
                """A dangerous class.

                Teaching:
                    gotcha: Never call without initialization.
                            (Evidence: test_dangerous.py::test_init_required)
                """
                pass
        ''')
        nodes = extractor.extract_module(source, "services.danger")
        teaching = nodes[0].teaching[0]
        assert "Never call without initialization" in teaching.insight
        assert teaching.evidence == "test_dangerous.py::test_init_required"

    def test_teaching_severity_detection(self, extractor: DocstringExtractor) -> None:
        """Severity inferred from keywords."""
        source = textwrap.dedent('''
            def critical_thing():
                """Do something.

                Teaching:
                    gotcha: You MUST always validate input.
                    gotcha: Be careful with edge cases.
                    gotcha: Consider caching for performance.
                """
                pass
        ''')
        nodes = extractor.extract_module(source, "services.test")
        teaching = nodes[0].teaching

        # MUST -> critical
        assert teaching[0].severity == "critical"
        # careful -> warning
        assert teaching[1].severity == "warning"
        # no keyword -> info
        assert teaching[2].severity == "info"

    # === Example Extraction ===

    def test_extract_doctest_examples(self, extractor: DocstringExtractor) -> None:
        """Extract >>> style examples."""
        source = textwrap.dedent('''
            def add(a: int, b: int) -> int:
                """Add two numbers.

                >>> add(1, 2)
                3
                >>> add(0, 0)
                0
                """
                return a + b
        ''')
        nodes = extractor.extract_module(source, "test")
        assert len(nodes[0].examples) >= 2
        assert "add(1, 2)" in nodes[0].examples

    def test_extract_example_section(self, extractor: DocstringExtractor) -> None:
        """Extract from Example: section."""
        source = textwrap.dedent('''
            def connect():
                """Connect to server.

                Example:
                    >>> conn = connect()
                    >>> conn.is_active
                    True
                """
                pass
        ''')
        nodes = extractor.extract_module(source, "test")
        assert len(nodes[0].examples) >= 1

    # === Tier Determination ===

    def test_tier_minimal_for_private(self, extractor: DocstringExtractor) -> None:
        """Private functions get MINIMAL tier."""
        source = textwrap.dedent("""
            def _private():
                pass
        """)
        nodes = extractor.extract_module(source, "test")
        assert nodes[0].tier == Tier.MINIMAL

    def test_tier_rich_for_services(self, extractor: DocstringExtractor) -> None:
        """Functions in services/ get RICH tier."""
        source = textwrap.dedent('''
            def public():
                """A public function."""
                pass
        ''')
        nodes = extractor.extract_module(source, "services.brain.persistence")
        assert nodes[0].tier == Tier.RICH

    def test_tier_standard_default(self, extractor: DocstringExtractor) -> None:
        """Default tier is STANDARD."""
        source = textwrap.dedent('''
            def regular():
                """A regular function."""
                pass
        ''')
        nodes = extractor.extract_module(source, "utils.helper")
        assert nodes[0].tier == Tier.STANDARD

    # === Signature Extraction ===

    def test_signature_function(self, extractor: DocstringExtractor) -> None:
        """Extract function signature."""
        source = textwrap.dedent('''
            def typed(x: int, y: str = "default") -> bool:
                """A typed function."""
                return True
        ''')
        nodes = extractor.extract_module(source, "test")
        sig = nodes[0].signature
        assert "def typed" in sig
        assert "x: int" in sig
        assert "y: str" in sig
        assert "-> bool" in sig

    def test_signature_async_function(self, extractor: DocstringExtractor) -> None:
        """Extract async function signature."""
        source = textwrap.dedent('''
            async def fetch(url: str) -> str:
                """Fetch a URL."""
                return ""
        ''')
        nodes = extractor.extract_module(source, "test")
        assert "async def fetch" in nodes[0].signature

    def test_signature_class(self, extractor: DocstringExtractor) -> None:
        """Extract class signature with bases."""
        source = textwrap.dedent('''
            class Child(Parent, Mixin):
                """A child class."""
                pass
        ''')
        nodes = extractor.extract_module(source, "test")
        assert "class Child(Parent, Mixin)" in nodes[0].signature

    # === Edge Cases ===

    def test_empty_source(self, extractor: DocstringExtractor) -> None:
        """Empty source returns empty list."""
        nodes = extractor.extract_module("", "test")
        assert nodes == []

    def test_syntax_error_returns_empty(self, extractor: DocstringExtractor) -> None:
        """Syntax errors return empty list (no crash)."""
        nodes = extractor.extract_module("def broken(", "test")
        assert nodes == []

    def test_no_docstring_skipped(self, extractor: DocstringExtractor) -> None:
        """Functions without docstrings are skipped (except MINIMAL)."""
        source = textwrap.dedent("""
            def no_docs():
                pass

            def _private_no_docs():
                pass
        """)
        nodes = extractor.extract_module(source, "utils")
        # no_docs skipped (STANDARD tier requires docstring)
        # _private_no_docs included (MINIMAL tier doesn't require docstring)
        assert len(nodes) == 1
        assert nodes[0].symbol == "_private_no_docs"


class TestExtractFromObject:
    """Tests for runtime object extraction."""

    def test_extract_from_function(self) -> None:
        """Extract DocNode from a function object."""

        def sample_function(x: int, y: str = "test") -> bool:
            """Sample function for testing.

            Teaching:
                gotcha: Always pass valid types.
            """
            return True

        node = extract_from_object(sample_function)
        assert node is not None
        assert node.symbol == "sample_function"
        assert "Sample function for testing" in node.summary


class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        summary=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\n\r\"'"),
        ).filter(lambda s: s.strip()),
    )
    @settings(max_examples=20)
    def test_summary_extraction_preserves_content(self, summary: str) -> None:
        """Extracted summary contains original content (modulo whitespace)."""
        # Skip summaries with problematic characters
        if '"""' in summary or "'''" in summary or "\n" in summary:
            return

        source = f'''
def test_func():
    """{summary}"""
    pass
'''
        extractor = DocstringExtractor()
        nodes = extractor.extract_module(source, "test")

        if nodes:  # May not parse if summary has special chars
            # Summary is first line, normalize whitespace for comparison
            expected = " ".join(summary.split())
            actual = " ".join(nodes[0].summary.split())
            assert expected == actual

    @given(
        symbol=st.from_regex(r"[a-z][a-z0-9_]*", fullmatch=True),
    )
    @settings(max_examples=20)
    def test_symbol_preserved(self, symbol: str) -> None:
        """Symbol name is preserved exactly."""
        source = f'''
def {symbol}():
    """A function."""
    pass
'''
        extractor = DocstringExtractor()
        nodes = extractor.extract_module(source, "test")
        assert len(nodes) == 1
        assert nodes[0].symbol == symbol


class TestLaws:
    """Verify Living Docs laws."""

    def test_provenance_law(self) -> None:
        """Law: evidence != None implies test reference format."""
        source = textwrap.dedent('''
            def verified():
                """A verified function.

                Teaching:
                    gotcha: Always validate.
                            (Evidence: test_verified.py::test_validation)
                """
                pass
        ''')
        extractor = DocstringExtractor()
        nodes = extractor.extract_module(source, "services.test")

        for node in nodes:
            for moment in node.teaching:
                if moment.evidence is not None:
                    # Evidence should be in test_file::test_name format
                    assert "::" in moment.evidence or moment.evidence.endswith(".py")
