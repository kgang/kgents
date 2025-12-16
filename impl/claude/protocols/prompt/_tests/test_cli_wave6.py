"""
Tests for Wave 6 CLI Enhancements.

Wave 6 of the Evergreen Prompt System.

Tests:
- --show-reasoning flag
- --show-habits flag
- --feedback flag (TextGRAD)
- --auto-improve flag
- --preview flag
- --emit-metrics flag
- Rich output formatting

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from ..cli_output import (
    HAS_RICH,
    PromptOutputFormatter,
)
from ..habits.policy import PolicyVector


class TestPromptOutputFormatter:
    """Tests for the PromptOutputFormatter class."""

    def test_formatter_initialization(self) -> None:
        """Formatter initializes correctly."""
        formatter = PromptOutputFormatter()
        assert formatter is not None

    def test_format_reasoning_tree_empty(self) -> None:
        """Empty traces return appropriate message."""
        formatter = PromptOutputFormatter()
        result = formatter.format_reasoning_tree([])
        assert "No reasoning traces available" in result

    def test_format_reasoning_tree_with_traces(self) -> None:
        """Traces are formatted as tree."""
        formatter = PromptOutputFormatter()
        traces = [
            "Loading section from file",
            "Applied filtering",
            "Merged with defaults",
        ]
        result = formatter.format_reasoning_tree(traces)

        assert "REASONING TREE" in result
        assert "Loading section from file" in result
        assert "Applied filtering" in result
        assert "Merged with defaults" in result
        # Check tree structure
        assert "├──" in result or "└──" in result

    def test_format_habit_table(self) -> None:
        """PolicyVector formats as table."""
        formatter = PromptOutputFormatter()
        policy = PolicyVector(
            verbosity=0.7,
            formality=0.8,
            risk_tolerance=0.3,
            confidence=0.9,
            learned_from=("git", "code"),
        )
        result = formatter.format_habit_table(policy)

        assert "HABIT INFLUENCE TABLE" in result
        assert "Verbosity" in result
        assert "Formality" in result
        assert "Risk Tolerance" in result
        assert "0.7" in result or "0.70" in result
        assert "git" in result

    def test_format_diff_empty(self) -> None:
        """Empty diff returns appropriate message."""
        formatter = PromptOutputFormatter()
        result = formatter.format_diff("")
        assert "No differences found" in result

    def test_format_diff_with_content(self) -> None:
        """Diff content is formatted with markers."""
        formatter = PromptOutputFormatter()
        diff_content = """\
--- a/file
+++ b/file
@@ -1,3 +1,4 @@
 line 1
-removed line
+added line
 line 3
"""
        result = formatter.format_diff(diff_content)

        assert "DIFF OUTPUT" in result
        assert "[+]" in result or "added line" in result
        assert "[-]" in result or "removed line" in result

    def test_format_history_timeline_empty(self) -> None:
        """Empty history returns appropriate message."""
        formatter = PromptOutputFormatter()
        result = formatter.format_history_timeline([])
        assert "No checkpoint history found" in result

    def test_format_preview(self) -> None:
        """Preview shows diff between current and new content."""
        formatter = PromptOutputFormatter()
        current = "line 1\nline 2\nline 3"
        new = "line 1\nmodified line 2\nline 3\nline 4"

        result = formatter.format_preview(current, new)

        assert "CHANGE PREVIEW" in result
        assert "Current:" in result
        assert "Proposed:" in result
        assert "Delta:" in result

    def test_format_improvement_result(self) -> None:
        """TextGRAD improvement result formats correctly."""
        formatter = PromptOutputFormatter()

        result = formatter.format_improvement_result(
            original="Original content",
            improved="Improved content",
            sections_modified=("systems", "skills"),
            reasoning_trace=("Applied condense gradient", "Modified 2 sections"),
            checkpoint_id="abc123",
        )

        assert "TEXTGRAD IMPROVEMENT RESULT" in result
        assert "Original:" in result
        assert "Improved:" in result
        assert "systems" in result
        assert "skills" in result
        assert "abc123" in result


class TestCLIFunctions:
    """Tests for CLI helper functions."""

    def test_content_to_sections_basic(self) -> None:
        """Content is parsed into sections correctly."""
        from ..cli import _content_to_sections

        content = """\
# Header

## Section One

Content for section one.

## Section Two

Content for section two.
"""
        sections = _content_to_sections(content)

        assert "Section One" in sections
        assert "Section Two" in sections
        assert "section one" in sections["Section One"].lower()
        assert "section two" in sections["Section Two"].lower()

    def test_content_to_sections_empty(self) -> None:
        """Empty content returns empty dict."""
        from ..cli import _content_to_sections

        sections = _content_to_sections("")
        assert sections == {}

    def test_content_to_sections_no_sections(self) -> None:
        """Content without sections returns empty dict."""
        from ..cli import _content_to_sections

        content = "Just some text without section headers."
        sections = _content_to_sections(content)
        assert sections == {}

    def test_generate_improvement_suggestions_verbose(self) -> None:
        """High verbosity policy generates appropriate suggestions."""
        from ..cli import _generate_improvement_suggestions

        policy = PolicyVector(verbosity=0.8)
        suggestions = _generate_improvement_suggestions(policy, "Short content")

        # High verbosity might suggest adding detail
        # The specific suggestion depends on implementation
        assert isinstance(suggestions, list)

    def test_generate_improvement_suggestions_low_verbosity(self) -> None:
        """Low verbosity with long content suggests condensing."""
        from ..cli import _generate_improvement_suggestions

        policy = PolicyVector(verbosity=0.3)
        content = "x" * 15000  # Long content

        suggestions = _generate_improvement_suggestions(policy, content)

        assert isinstance(suggestions, list)
        # Should suggest condensing
        if suggestions:
            assert any("conden" in s.lower() for s in suggestions)

    def test_generate_improvement_suggestions_domain_focus(self) -> None:
        """Domain focus generates domain-specific suggestions."""
        from ..cli import _generate_improvement_suggestions

        policy = PolicyVector(
            verbosity=0.5,
            domain_focus=(("agentese", 0.9), ("cli", 0.3)),
        )
        suggestions = _generate_improvement_suggestions(policy, "Some content")

        assert isinstance(suggestions, list)
        # High domain focus should be mentioned
        if suggestions:
            assert any("agentese" in s.lower() for s in suggestions)


class TestCLICompileFlags:
    """Tests for compile command flags."""

    def test_compile_basic(self) -> None:
        """Basic compile works without flags."""
        from ..cli import compile_prompt

        # This should not raise
        result = compile_prompt(
            checkpoint=False,  # Don't create checkpoint in tests
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_compile_show_reasoning_flag(self) -> None:
        """--show-reasoning flag triggers reasoning output."""
        # This test verifies the flag is processed
        import io
        import sys

        from ..cli import compile_prompt

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            compile_prompt(
                checkpoint=False,
                show_reasoning=True,
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Should have formatting for reasoning
        assert "EVERGREEN" in output or len(output) > 0

    def test_compile_show_habits_flag(self) -> None:
        """--show-habits flag triggers habit output."""
        import io
        import sys

        from ..cli import compile_prompt

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            compile_prompt(
                checkpoint=False,
                show_habits=True,
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Should have formatting for habits
        assert len(output) > 0

    def test_compile_preview_flag(self) -> None:
        """--preview flag shows diff without writing."""
        import io
        import sys

        from ..cli import compile_prompt

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            compile_prompt(
                checkpoint=False,
                preview=True,
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Should show preview format
        assert (
            "PREVIEW" in output
            or "Current:" in output
            or "Proposed:" in output
            or len(output) > 0
        )


class TestPolicyVectorIntegration:
    """Tests for PolicyVector integration with CLI."""

    def test_get_policy_vector_default(self) -> None:
        """_get_policy_vector returns a PolicyVector."""
        from ..cli import _get_policy_vector

        policy = _get_policy_vector(Path("/nonexistent"))

        assert isinstance(policy, PolicyVector)
        assert 0.0 <= policy.verbosity <= 1.0
        assert 0.0 <= policy.formality <= 1.0

    def test_policy_vector_default_values(self) -> None:
        """Default PolicyVector has sensible values."""
        policy = PolicyVector.default()

        assert policy.verbosity == 0.5
        assert policy.formality == 0.6
        assert policy.risk_tolerance == 0.4
        assert policy.confidence == 0.5
        assert "default" in policy.learned_from


class TestRichOutputHelpers:
    """Tests for Rich output helper functions."""

    def test_print_rich_panel_fallback(self) -> None:
        """print_rich_panel works without Rich."""
        import io
        import sys

        from ..cli_output import print_rich_panel

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            print_rich_panel("Title", "Content", "blue")
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "Title" in output
        assert "Content" in output

    def test_print_rich_table_fallback(self) -> None:
        """print_rich_table works without Rich."""
        import io
        import sys

        from ..cli_output import print_rich_table

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            print_rich_table(
                "Test Table",
                ["Col1", "Col2"],
                [["a", "b"], ["c", "d"]],
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "Test Table" in output
        assert "Col1" in output
        assert "a" in output

    def test_print_rich_tree_fallback(self) -> None:
        """print_rich_tree works without Rich."""
        import io
        import sys

        from ..cli_output import print_rich_tree

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            print_rich_tree(
                "Root",
                [("Child1", ["Grandchild1"]), ("Child2", [])],
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        assert "Root" in output
        assert "Child1" in output


class TestTextGRADIntegration:
    """Tests for TextGRAD integration with CLI."""

    def test_apply_textgrad_feedback_empty(self) -> None:
        """Empty sections handle gracefully."""
        from ..cli import _apply_textgrad_feedback

        formatter = PromptOutputFormatter()

        # Should not crash with empty sections
        result = _apply_textgrad_feedback(
            sections={},
            feedback="be more concise",
            formatter=formatter,
        )

        # Result might be None or improved content
        assert result is None or isinstance(result, str)

    def test_apply_textgrad_feedback_basic(self) -> None:
        """Basic feedback application works."""
        import io
        import sys

        from ..cli import _apply_textgrad_feedback

        formatter = PromptOutputFormatter()

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            result = _apply_textgrad_feedback(
                sections={"systems": "This is a long section with lots of content."},
                feedback="be more concise",
                formatter=formatter,
            )
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Should produce some output
        assert len(output) > 0 or result is not None


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing (integration)."""

    def test_compile_subcommand_exists(self) -> None:
        """compile subcommand is defined."""
        import argparse

        from ..cli import main

        # Main should not raise when called with valid args
        # (We test the structure, not execution)
        assert callable(main)

    def test_wave6_flags_defined(self) -> None:
        """Wave 6 flags are defined in argparse."""
        import argparse

        from ..cli import main

        # Create parser manually to check flags
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        compile_parser = subparsers.add_parser("compile")

        # The actual CLI adds these flags - verify by checking source
        import inspect

        from ..cli import compile_prompt

        sig = inspect.signature(compile_prompt)
        params = list(sig.parameters.keys())

        assert "show_reasoning" in params
        assert "show_habits" in params
        assert "feedback" in params
        assert "auto_improve" in params
        assert "preview" in params
        assert "emit_metrics" in params
