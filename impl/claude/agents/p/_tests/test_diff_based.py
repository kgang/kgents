"""Tests for DiffBasedParser (Phase 3: Novel Techniques)."""

from __future__ import annotations

from agents.p.strategies.diff_based import (
    DiffBasedParser,
    create_egent_diff_parser,
    create_wgent_diff_parser,
)


class TestUnifiedDiff:
    """Test unified diff format parsing."""

    def test_simple_unified_diff(self) -> None:
        """Test basic unified diff application."""
        base = "line1\nline2\nline3"
        parser = DiffBasedParser(base_template=base)

        diff = """
--- original
+++ modified
@@ -1,3 +1,3 @@
 line1
-line2
+LINE2
 line3
"""
        result = parser.parse(diff)
        assert result.success
        assert result.value is not None
        assert "LINE2" in result.value
        assert result.confidence >= 0.8

    def test_unified_diff_with_context(self) -> None:
        """Test unified diff with context lines."""
        base = "a\nb\nc\nd"
        parser = DiffBasedParser(base_template=base)

        diff = """
--- original
+++ modified
@@ -1,4 +1,4 @@
 a
-b
+B
 c
 d
"""
        result = parser.parse(diff)
        assert result.success
        assert result.value is not None
        assert "B" in result.value

    def test_unified_diff_not_present(self) -> None:
        """Test non-unified diff fails gracefully."""
        parser = DiffBasedParser(base_template="hello")
        result = parser.parse("not a diff")
        assert not result.success


class TestSimpleReplacement:
    """Test sed-style replacements."""

    def test_sed_format(self) -> None:
        """Test s/old/new/ format."""
        parser = DiffBasedParser(base_template="Hello World")
        diff = "s/World/Universe/"
        result = parser.parse(diff)

        assert result.success
        assert result.value == "Hello Universe"
        assert result.confidence >= 0.85
        assert result.strategy is not None
        assert "sed-replacement" in result.strategy

    def test_replace_with_format(self) -> None:
        """Test 'Replace X with Y' format."""
        parser = DiffBasedParser(base_template="foo bar baz")
        diff = 'Replace "bar" with "BAR"'
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "BAR" in result.value
        assert result.confidence >= 0.8

    def test_arrow_notation(self) -> None:
        """Test old -> new notation."""
        parser = DiffBasedParser(base_template="<div>test</div>")
        diff = "test -> TEST"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "TEST" in result.value

    def test_replacement_not_found(self) -> None:
        """Test replacement when target not in base."""
        parser = DiffBasedParser(base_template="hello")
        diff = "s/goodbye/bye/"
        result = parser.parse(diff)

        # Should fail since "goodbye" not in base
        assert not result.success


class TestLinePatch:
    """Test line-based patches."""

    def test_replace_line_with(self) -> None:
        """Test 'Replace line N with: X' format."""
        base = "line1\nline2\nline3"
        parser = DiffBasedParser(base_template=base)
        diff = "Replace line 2 with: LINE2"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "LINE2" in result.value
        lines = result.value.split("\n")
        assert lines[1] == "LINE2"

    def test_line_notation(self) -> None:
        """Test 'Line N: X' format."""
        base = "a\nb\nc"
        parser = DiffBasedParser(base_template=base)
        diff = "Line 2: B"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "B" in result.value

    def test_at_notation(self) -> None:
        """Test '@N: X' format."""
        base = "one\ntwo\nthree"
        parser = DiffBasedParser(base_template=base)
        diff = "@2: TWO"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "TWO" in result.value

    def test_line_out_of_range(self) -> None:
        """Test line number out of range."""
        parser = DiffBasedParser(base_template="a\nb")
        diff = "Replace line 5 with: X"
        result = parser.parse(diff)

        # Should fail gracefully
        assert not result.success


class TestFallbackChain:
    """Test that parser tries multiple formats."""

    def test_tries_all_formats(self) -> None:
        """Test parser falls back through formats."""
        parser = DiffBasedParser(base_template="hello world")

        # This should work via simple replacement
        diff = "s/world/universe/"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "universe" in result.value

    def test_failure_after_all_attempts(self) -> None:
        """Test that unrecognized format fails."""
        parser = DiffBasedParser(base_template="test")
        diff = "completely invalid diff format xyz"
        result = parser.parse(diff)

        assert not result.success
        assert result.error is not None
        assert "Could not parse diff" in result.error


class TestConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self) -> None:
        """Test configure returns new instance."""
        parser1 = DiffBasedParser(base_template="test")
        parser2 = parser1.configure(min_confidence=0.9)

        assert parser1 is not parser2
        assert parser2.config.min_confidence == 0.9

    def test_fuzz_factor(self) -> None:
        """Test fuzz factor configuration."""
        parser = DiffBasedParser(base_template="test", fuzz_factor=5)
        assert parser.fuzz_factor == 5


class TestConvenienceFunctions:
    """Test convenience parser constructors."""

    def test_wgent_diff_parser(self) -> None:
        """Test W-gent HTML diff parser."""
        html = '<html><body><div id="main">Hello</div></body></html>'
        parser = create_wgent_diff_parser(html)

        diff = "s/Hello/Hello World/"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "Hello World" in result.value
        assert parser.fuzz_factor == 3  # Configured for HTML

    def test_egent_diff_parser(self) -> None:
        """Test E-gent code diff parser."""
        code = "def foo() -> None:\n    pass"
        parser = create_egent_diff_parser(code)

        diff = "s/pass/return 42/"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "return 42" in result.value
        assert parser.fuzz_factor == 1  # Strict for code


class TestStreamParsing:
    """Test stream parsing (should buffer)."""

    def test_stream_buffers_and_parses(self) -> None:
        """Test stream parsing buffers tokens."""
        parser = DiffBasedParser(base_template="hello")
        tokens = ["s/", "hello", "/", "world", "/"]
        results = list(parser.parse_stream(iter(tokens)))

        assert len(results) == 1
        assert results[0].success
        assert results[0].value is not None
        assert "world" in results[0].value


class TestRepairTracking:
    """Test that repairs are tracked."""

    def test_repairs_tracked_in_result(self) -> None:
        """Test repairs are logged."""
        parser = DiffBasedParser(base_template="test")
        diff = "s/test/TEST/"
        result = parser.parse(diff)

        assert result.success
        assert len(result.repairs) > 0
        assert "sed replacement" in result.repairs[0].lower()

    def test_multiple_repairs_logged(self) -> None:
        """Test multiple repair steps logged."""
        base = "line1\nline2\nline3"
        parser = DiffBasedParser(base_template=base)
        diff = "Replace line 2 with: LINE2"
        result = parser.parse(diff)

        assert result.success
        assert len(result.repairs) > 0


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_wgent_html_update(self) -> None:
        """Test W-gent HTML incremental update."""
        base = """
<html>
<head><title>Dashboard</title></head>
<body>
  <div id="main">Loading...</div>
</body>
</html>
"""
        parser = create_wgent_diff_parser(base)
        diff = "s/Loading.../Status: Running/"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "Status: Running" in result.value
        assert "Loading..." not in result.value

    def test_egent_code_evolution(self) -> None:
        """Test E-gent code evolution via diff."""
        base = """
def process(data) -> None:
    # TODO: implement
    pass
"""
        parser = create_egent_diff_parser(base)
        diff = "s/pass/return [x * 2 for x in data]/"
        result = parser.parse(diff)

        assert result.success
        assert result.value is not None
        assert "return [x * 2 for x in data]" in result.value
        assert "pass" not in result.value
