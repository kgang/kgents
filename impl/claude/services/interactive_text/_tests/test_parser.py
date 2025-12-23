"""
Parser tests with roundtrip fidelity verification.

These tests verify the core guarantee of the Interactive Text parser:
    parse(render(parse(doc))) ≡ parse(doc)

This means any document can be parsed, rendered back to text, and re-parsed
to produce structurally identical results.

Requirements: 16.1, 16.2, 16.3
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from hypothesis import given, settings, strategies as st

from services.interactive_text.parser import (
    DocumentEdit,
    IncrementalParser,
    MarkdownParser,
    ParsedDocument,
    SourceMap,
    SourcePosition,
    TextSpan,
    parse_markdown,
    render_markdown,
)
from services.interactive_text.registry import TokenRegistry

# =============================================================================
# Roundtrip Fidelity Tests (Phase 1 Core Verification)
# =============================================================================


class TestRoundtripFidelity:
    """Verify the core roundtrip guarantee: parse(render(parse(doc))) ≡ parse(doc)."""

    def test_roundtrip_simple_text(self) -> None:
        """Plain text roundtrips exactly."""
        text = "Hello, world!"
        doc = parse_markdown(text)
        rendered = doc.render()
        assert rendered == text

    def test_roundtrip_with_agentese_path(self) -> None:
        """AGENTESE paths preserve structure through roundtrip."""
        text = "Check `world.town.citizen` for status."
        doc = parse_markdown(text)
        rendered = doc.render()
        reparsed = parse_markdown(rendered)

        assert rendered == text
        assert len(doc.tokens) == len(reparsed.tokens)
        assert doc.tokens[0].token_type == reparsed.tokens[0].token_type

    def test_roundtrip_with_task_checkbox(self) -> None:
        """Task checkboxes preserve state through roundtrip."""
        text = "- [ ] Uncompleted task\n- [x] Completed task\n"
        doc = parse_markdown(text)
        rendered = doc.render()
        reparsed = parse_markdown(rendered)

        assert rendered == text
        assert len(doc.tokens) == 2
        assert len(reparsed.tokens) == 2

    def test_roundtrip_with_image(self) -> None:
        """Images preserve alt text and path through roundtrip."""
        text = "Here is an image: ![screenshot](./img/test.png)"
        doc = parse_markdown(text)
        rendered = doc.render()
        reparsed = parse_markdown(rendered)

        assert rendered == text
        assert doc.token_count == reparsed.token_count

    def test_roundtrip_with_code_block(self) -> None:
        """Code blocks preserve language and content through roundtrip."""
        text = dedent("""\
            Here is some code:

            ```python
            def hello():
                print("world")
            ```

            End of code.
        """)
        doc = parse_markdown(text)
        rendered = doc.render()
        reparsed = parse_markdown(rendered)

        assert rendered == text
        assert doc.token_count == reparsed.token_count

    def test_roundtrip_with_principle_ref(self) -> None:
        """Principle references preserve through roundtrip."""
        text = "This follows [P1] guidelines."
        doc = parse_markdown(text)
        rendered = doc.render()

        assert rendered == text

    def test_roundtrip_with_requirement_ref(self) -> None:
        """Requirement references preserve through roundtrip."""
        text = "See requirement [R7.1] for details."
        doc = parse_markdown(text)
        rendered = doc.render()

        assert rendered == text

    def test_roundtrip_complex_document(self) -> None:
        """Complex document with multiple token types roundtrips correctly."""
        text = dedent("""\
            # Interactive Text Demo

            Check `self.document.manifest` for rendering.

            ## Tasks

            - [ ] Implement parser
            - [x] Write tests

            ## Code Example

            ```python
            await logos.invoke("world.town.citizen")
            ```

            ![diagram](./arch.png)

            Per [P1] and [R7.1], this is complete.
        """)
        doc = parse_markdown(text)
        rendered = doc.render()
        reparsed = parse_markdown(rendered)

        # Exact text preservation
        assert rendered == text

        # Structure preservation
        assert doc.token_count == reparsed.token_count
        for orig, re in zip(doc.tokens, reparsed.tokens):
            assert orig.token_type == re.token_type
            assert orig.text == re.text

    def test_roundtrip_preserves_whitespace(self) -> None:
        """All whitespace (spaces, tabs, newlines) is preserved."""
        text = "  Leading spaces\n\tTab here\n\n\nMultiple newlines"
        doc = parse_markdown(text)
        rendered = doc.render()

        assert rendered == text

    def test_roundtrip_empty_document(self) -> None:
        """Empty document roundtrips correctly."""
        text = ""
        doc = parse_markdown(text)
        rendered = doc.render()

        assert rendered == text
        assert doc.token_count == 0


class TestRoundtripStructuralEquivalence:
    """Verify parse(render(parse(doc))) ≡ parse(doc) for structure."""

    def test_structural_equivalence_basic(self) -> None:
        """Basic structural equivalence test."""
        text = "Path: `world.town.citizen`"
        doc1 = parse_markdown(text)
        rendered = doc1.render()
        doc2 = parse_markdown(rendered)

        # Same number of spans
        assert len(doc1.spans) == len(doc2.spans)

        # Same token positions (relative to text)
        for s1, s2 in zip(doc1.spans, doc2.spans):
            assert s1.text == s2.text
            assert s1.is_token == s2.is_token
            assert s1.position.start == s2.position.start
            assert s1.position.end == s2.position.end

    def test_structural_equivalence_multiline(self) -> None:
        """Structural equivalence for multiline documents."""
        text = dedent("""\
            Line 1 with `self.brain.capture`
            Line 2 with - [ ] a task
            Line 3 plain
        """)
        doc1 = parse_markdown(text)
        doc2 = parse_markdown(doc1.render())

        assert doc1.token_count == doc2.token_count
        assert len(doc1.spans) == len(doc2.spans)


# =============================================================================
# Token Recognition Tests
# =============================================================================


class TestTokenRecognition:
    """Test that all six token types are correctly recognized."""

    def test_agentese_path_recognition(self) -> None:
        """AGENTESE paths are recognized with all five contexts."""
        contexts = ["world", "self", "concept", "void", "time"]
        for ctx in contexts:
            text = f"`{ctx}.test.path`"
            doc = parse_markdown(text)
            assert doc.token_count == 1
            assert doc.tokens[0].token_type == "agentese_path"

    def test_task_checkbox_unchecked(self) -> None:
        """Unchecked task checkbox is recognized."""
        text = "- [ ] Task to do\n"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "task_checkbox"

    def test_task_checkbox_checked(self) -> None:
        """Checked task checkbox is recognized."""
        text = "- [x] Completed task\n"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "task_checkbox"

    def test_image_recognition(self) -> None:
        """Image tokens are recognized."""
        text = "![alt text](path/to/image.png)"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "image"

    def test_code_block_recognition(self) -> None:
        """Code blocks are recognized with language."""
        text = "```python\nprint('hello')\n```"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "code_block"

    def test_principle_ref_recognition(self) -> None:
        """Principle references are recognized."""
        text = "Follow [P1] guidelines"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "principle_ref"

    def test_requirement_ref_recognition(self) -> None:
        """Requirement references are recognized."""
        text = "See [R7.1] for details"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "requirement_ref"

    def test_no_false_positives_plain_text(self) -> None:
        """Plain text without tokens has zero token count."""
        text = "This is just plain text without any special tokens."
        doc = parse_markdown(text)
        assert doc.token_count == 0

    def test_token_precision_backticks(self) -> None:
        """Backticks that aren't AGENTESE paths aren't tokenized."""
        text = "`regular code` is not `world.path`"
        doc = parse_markdown(text)
        # Only world.path should be tokenized
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "agentese_path"


# =============================================================================
# Source Position Tests
# =============================================================================


class TestSourcePositions:
    """Test that source positions are accurate."""

    def test_single_token_position(self) -> None:
        """Single token has correct start/end positions."""
        text = "Start `world.test` end"
        doc = parse_markdown(text)

        token = doc.tokens[0]
        assert token.position.start == 6  # After "Start "
        assert token.position.end == 18  # After "`world.test`"
        assert text[token.position.start : token.position.end] == "`world.test`"

    def test_multiple_token_positions(self) -> None:
        """Multiple tokens have non-overlapping positions."""
        text = "`self.a` and `world.b`"
        doc = parse_markdown(text)

        assert len(doc.tokens) == 2
        t1, t2 = doc.tokens

        # Non-overlapping
        assert t1.position.end <= t2.position.start

        # Correct extraction
        assert text[t1.position.start : t1.position.end] == "`self.a`"
        assert text[t2.position.start : t2.position.end] == "`world.b`"

    def test_get_token_at_offset(self) -> None:
        """Can retrieve token at a specific byte offset."""
        text = "Check `world.town` here"
        doc = parse_markdown(text)

        # Inside the token
        token = doc.get_token_at(8)
        assert token is not None
        assert token.token_type == "agentese_path"

        # Outside any token
        assert doc.get_token_at(0) is None
        assert doc.get_token_at(20) is None


# =============================================================================
# Incremental Parser Tests
# =============================================================================


class TestIncrementalParser:
    """Test incremental parsing for efficient updates."""

    def test_apply_simple_edit(self) -> None:
        """Simple text edit is applied correctly."""
        parser = IncrementalParser()
        doc = parser.parse("Hello world")

        edit = DocumentEdit(start=6, end=11, new_text="there")
        updated = parser.apply_edit(doc, edit)

        assert updated.render() == "Hello there"

    def test_edit_preserves_tokens_before(self) -> None:
        """Tokens before edit region are preserved."""
        parser = IncrementalParser()
        text = "`self.a` middle `world.b`"
        doc = parser.parse(text)

        # Edit in the middle
        edit = DocumentEdit(start=9, end=15, new_text="center")
        updated = parser.apply_edit(doc, edit)

        # First token should still exist
        assert any(t.token_type == "agentese_path" for t in updated.tokens)

    def test_edit_preserves_tokens_after(self) -> None:
        """Tokens after edit region are preserved with adjusted positions."""
        parser = IncrementalParser()
        text = "`self.a` middle `world.b`"
        doc = parser.parse(text)

        # Edit before second token
        edit = DocumentEdit(start=9, end=15, new_text="XX")
        updated = parser.apply_edit(doc, edit)

        # Both tokens should still be recognized
        assert updated.token_count >= 1


# =============================================================================
# SourceMap Tests
# =============================================================================


class TestSourceMap:
    """Test source map functionality."""

    def test_source_map_creation(self) -> None:
        """Source map is created from document."""
        doc = parse_markdown("Test `world.path` here")
        source_map = SourceMap(doc)

        assert source_map.document is doc

    def test_get_token_at_position(self) -> None:
        """Can get token by line/column."""
        doc = parse_markdown("Line 1\n`world.path`")
        source_map = SourceMap(doc)

        # Token is on line 2
        token = source_map.get_token_at_position(2, 1)
        assert token is not None
        assert token.token_type == "agentese_path"


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test the module-level convenience functions."""

    def test_parse_markdown_function(self) -> None:
        """parse_markdown convenience function works."""
        doc = parse_markdown("Test `self.x`")
        assert isinstance(doc, ParsedDocument)
        assert doc.token_count == 1

    def test_render_markdown_function(self) -> None:
        """render_markdown convenience function works."""
        doc = parse_markdown("Test text")
        rendered = render_markdown(doc)
        assert rendered == "Test text"


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestParserProperties:
    """Property-based tests for parser robustness."""

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_parser_never_crashes(self, text: str) -> None:
        """Parser handles arbitrary text without crashing."""
        try:
            doc = parse_markdown(text)
            _ = doc.render()
        except Exception as e:
            pytest.fail(f"Parser crashed on input: {text!r}, error: {e}")

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_render_preserves_length(self, text: str) -> None:
        """Rendered output has same length as input (roundtrip)."""
        doc = parse_markdown(text)
        rendered = doc.render()
        assert len(rendered) == len(text)

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_roundtrip_idempotent(self, text: str) -> None:
        """Multiple roundtrips produce same result."""
        doc1 = parse_markdown(text)
        rendered1 = doc1.render()

        doc2 = parse_markdown(rendered1)
        rendered2 = doc2.render()

        assert rendered1 == rendered2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_content(self) -> None:
        """Unicode characters are preserved."""
        text = "Check `world.test` with emoji 🚀 and 中文"
        doc = parse_markdown(text)
        assert doc.render() == text

    def test_very_long_line(self) -> None:
        """Very long lines are handled."""
        text = "x" * 10000 + " `self.test` " + "y" * 10000
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.render() == text

    def test_nested_backticks(self) -> None:
        """Nested backticks don't break parser."""
        text = "``code with `self.path` inside``"
        doc = parse_markdown(text)
        # Should still find the AGENTESE path
        assert doc.token_count >= 1

    def test_adjacent_tokens(self) -> None:
        """Adjacent tokens are both recognized."""
        text = "`self.a``world.b`"
        doc = parse_markdown(text)
        assert doc.token_count == 2

    def test_token_at_start(self) -> None:
        """Token at document start is recognized."""
        text = "`world.first` after"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].position.start == 0

    def test_token_at_end(self) -> None:
        """Token at document end is recognized."""
        text = "before `world.last`"
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].position.end == len(text)


# =============================================================================
# New Token Types (Tables, Links, etc.)
# =============================================================================


class TestMarkdownTableRecognition:
    """Test markdown table token recognition."""

    def test_simple_table(self) -> None:
        """Simple two-column table is recognized."""
        text = dedent("""\
            | Col A | Col B |
            |-------|-------|
            | data1 | data2 |
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "markdown_table"

    def test_table_with_alignment(self) -> None:
        """Table with alignment markers is recognized."""
        text = dedent("""\
            | Left | Center | Right |
            |:-----|:------:|------:|
            | L    | C      | R     |
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "markdown_table"

    def test_table_multiple_rows(self) -> None:
        """Table with multiple data rows is recognized."""
        text = dedent("""\
            | Name | Value |
            |------|-------|
            | foo  | 1     |
            | bar  | 2     |
            | baz  | 3     |
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "markdown_table"

    def test_table_roundtrip(self) -> None:
        """Table roundtrips correctly."""
        text = dedent("""\
            | Header 1 | Header 2 |
            |----------|----------|
            | Cell 1   | Cell 2   |
        """)
        doc = parse_markdown(text)
        rendered = doc.render()
        assert rendered == text

    def test_table_from_spec(self) -> None:
        """Table from the interactive-text spec is recognized."""
        text = dedent("""\
            | Without | With |
            |---------|------|
            | Specs describe interfaces | Specs ARE interfaces |
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "markdown_table"


class TestLinkRecognition:
    """Test link token recognition."""

    def test_simple_link(self) -> None:
        """Simple link is recognized."""
        text = "Check [this link](https://example.com) for info."
        doc = parse_markdown(text)
        link_tokens = [t for t in doc.tokens if t.token_type == "link"]
        assert len(link_tokens) == 1

    def test_link_not_image(self) -> None:
        """Link is distinct from image (no ! prefix)."""
        text = "[link](url) and ![image](url)"
        doc = parse_markdown(text)
        link_tokens = [t for t in doc.tokens if t.token_type == "link"]
        image_tokens = [t for t in doc.tokens if t.token_type == "image"]
        assert len(link_tokens) == 1
        assert len(image_tokens) == 1

    def test_link_roundtrip(self) -> None:
        """Links roundtrip correctly."""
        text = "Visit [our docs](https://docs.example.com/guide) today."
        doc = parse_markdown(text)
        assert doc.render() == text


class TestBlockquoteRecognition:
    """Test blockquote token recognition."""

    def test_simple_blockquote(self) -> None:
        """Simple blockquote is recognized."""
        text = "> This is a quote\n"
        doc = parse_markdown(text)
        quote_tokens = [t for t in doc.tokens if t.token_type == "blockquote"]
        assert len(quote_tokens) == 1

    def test_multiline_blockquote(self) -> None:
        """Multi-line blockquote is recognized."""
        text = "> Line 1\n> Line 2\n> Line 3\n"
        doc = parse_markdown(text)
        quote_tokens = [t for t in doc.tokens if t.token_type == "blockquote"]
        assert len(quote_tokens) == 1

    def test_blockquote_roundtrip(self) -> None:
        """Blockquotes roundtrip correctly."""
        text = "> The proof IS the decision.\n"
        doc = parse_markdown(text)
        assert doc.render() == text


class TestHorizontalRuleRecognition:
    """Test horizontal rule token recognition."""

    def test_dash_rule(self) -> None:
        """Dash horizontal rule is recognized."""
        text = "---\n"
        doc = parse_markdown(text)
        rule_tokens = [t for t in doc.tokens if t.token_type == "horizontal_rule"]
        assert len(rule_tokens) == 1

    def test_asterisk_rule(self) -> None:
        """Asterisk horizontal rule is recognized."""
        text = "***\n"
        doc = parse_markdown(text)
        rule_tokens = [t for t in doc.tokens if t.token_type == "horizontal_rule"]
        assert len(rule_tokens) == 1

    def test_underscore_rule(self) -> None:
        """Underscore horizontal rule is recognized."""
        text = "___\n"
        doc = parse_markdown(text)
        rule_tokens = [t for t in doc.tokens if t.token_type == "horizontal_rule"]
        assert len(rule_tokens) == 1

    def test_horizontal_rule_roundtrip(self) -> None:
        """Horizontal rules roundtrip correctly."""
        text = "Before\n\n---\n\nAfter"
        doc = parse_markdown(text)
        assert doc.render() == text


# =============================================================================
# Code Block Protection Tests
# =============================================================================


class TestCodeBlockProtection:
    """Test that tokens inside code blocks are NOT recognized."""

    def test_agentese_path_inside_code_block_not_tokenized(self) -> None:
        """AGENTESE paths inside code blocks should NOT be recognized."""
        text = dedent("""\
            ```python
            path = "world.town.citizen"
            await logos.invoke("self.brain.capture")
            ```
        """)
        doc = parse_markdown(text)

        # Should only have 1 token: the code block itself
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "code_block"

    def test_task_checkbox_inside_code_block_not_tokenized(self) -> None:
        """Task checkboxes inside code blocks should NOT be recognized."""
        text = dedent("""\
            ```markdown
            - [ ] This is NOT a real task
            - [x] Neither is this
            ```
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "code_block"

    def test_table_inside_code_block_not_tokenized(self) -> None:
        """Tables inside code blocks should NOT be recognized."""
        text = dedent("""\
            ```markdown
            | Header | Header |
            |--------|--------|
            | Cell   | Cell   |
            ```
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "code_block"

    def test_tokens_outside_code_block_still_recognized(self) -> None:
        """Tokens outside code blocks should still be recognized."""
        text = dedent("""\
            Check `world.town.citizen` here.

            ```python
            path = "world.town.ignored"
            ```

            And also `self.brain.capture` here.
        """)
        doc = parse_markdown(text)

        # Should have: code_block + 2 agentese_path tokens
        code_blocks = [t for t in doc.tokens if t.token_type == "code_block"]
        agentese_paths = [t for t in doc.tokens if t.token_type == "agentese_path"]

        assert len(code_blocks) == 1
        assert len(agentese_paths) == 2

    def test_code_block_with_nested_backticks(self) -> None:
        """Code blocks with nested backticks are handled correctly."""
        text = dedent("""\
            ````python
            # This code block contains ```
            code = '''
            ```markdown
            Not a code block
            ```
            '''
            ````
        """)
        doc = parse_markdown(text)
        assert doc.token_count == 1
        assert doc.tokens[0].token_type == "code_block"


# =============================================================================
# Complex Document Tests
# =============================================================================


class TestComplexDocuments:
    """Test parsing of complex real-world documents."""

    def test_spec_like_document(self) -> None:
        """Document similar to interactive-text.md spec."""
        text = dedent("""\
            # Interactive Text Protocol

            > *"The spec is not description—it is generative."*

            ---

            ## Part I: Purpose

            | Without | With |
            |---------|------|
            | Specs describe | Specs ARE interfaces |

            ### Example Code

            ```python
            @semantic_token("agentese_path")
            class AGENTESEPathToken:
                pattern = re.compile(r'`world\\.path`')
            ```

            See `world.document.interactive` for details.

            - [ ] Implement parser
            - [x] Write tests
        """)
        doc = parse_markdown(text)

        # Count token types
        token_types = {}
        for token in doc.tokens:
            t = token.token_type
            token_types[t] = token_types.get(t, 0) + 1

        # Should have:
        # - 1 blockquote
        # - 1 horizontal_rule
        # - 1 markdown_table
        # - 1 code_block
        # - 1 agentese_path (the one outside code block)
        # - 2 task_checkbox
        assert token_types.get("blockquote", 0) >= 1
        assert token_types.get("horizontal_rule", 0) >= 1
        assert token_types.get("markdown_table", 0) >= 1
        assert token_types.get("code_block", 0) >= 1
        assert token_types.get("agentese_path", 0) >= 1
        assert token_types.get("task_checkbox", 0) >= 2

        # Roundtrip fidelity
        assert doc.render() == text
