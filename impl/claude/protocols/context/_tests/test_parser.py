"""
Tests for the Context Perception Parser.

These tests verify token recognition and invisible metadata handling.

Spec: spec/protocols/context-perception.md §7
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ..parser import (
    METADATA_MARKER,
    RecognizedToken,
    TokenType,
    decode_invisible_metadata,
    encode_invisible_metadata,
    extract_portal_info,
    extract_tokens,
    is_agentese_path,
    is_portal_line,
    parse_text,
)

# === Token Extraction Tests ===


class TestExtractTokens:
    """Tests for extract_tokens() function."""

    def test_portal_collapsed(self) -> None:
        """Recognize collapsed portal."""
        text = "▶ [tests] ──→ 3 files"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.PORTAL_COLLAPSED
        assert token.edge_type == "tests"
        assert token.summary == "3 files"

    def test_portal_collapsed_simple(self) -> None:
        """Recognize collapsed portal without arrow."""
        text = "▶ [implements] auth_spec.md"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.PORTAL_COLLAPSED
        assert tokens[0].edge_type == "implements"

    def test_portal_expanded(self) -> None:
        """Recognize expanded portal."""
        text = "▼ [tests] ──→ 3 files"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.PORTAL_EXPANDED
        assert token.edge_type == "tests"

    def test_portal_expanded_no_summary(self) -> None:
        """Recognize expanded portal without summary."""
        text = "▼ [imports]"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.PORTAL_EXPANDED
        assert tokens[0].edge_type == "imports"

    def test_agentese_path(self) -> None:
        """Recognize AGENTESE path."""
        text = "Check `world.auth.middleware` for details"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.AGENTESE_PATH
        assert token.path == "world.auth.middleware"

    def test_agentese_self_path(self) -> None:
        """Recognize self.* AGENTESE path."""
        text = "Use `self.context.manifest` to see state"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].path == "self.context.manifest"

    def test_task_checkbox_unchecked(self) -> None:
        """Recognize unchecked task."""
        text = "[ ] Implement the feature"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.TASK_CHECKBOX
        assert token.is_checked is False

    def test_task_checkbox_checked(self) -> None:
        """Recognize checked task."""
        text = "[x] Complete the tests"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].is_checked is True

    def test_evidence_link(self) -> None:
        """Recognize evidence link."""
        text = "📎 Token validation is correct"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.EVIDENCE_LINK
        assert token.claim == "Token validation is correct"

    def test_evidence_link_with_strength(self) -> None:
        """Recognize evidence link with strength."""
        text = "📎 Auth bug found (strong)"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].claim == "Auth bug found"
        assert tokens[0].evidence_strength == "strong"

    def test_annotation(self) -> None:
        """Recognize annotation."""
        text = "💭 This looks suspicious"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.ANNOTATION

    def test_agent_mention(self) -> None:
        """Recognize agent mention."""
        text = "Hey @Claude, can you check this?"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.token_type == TokenType.AGENT_MENTION
        assert token.agent_name == "Claude"

    def test_code_fence(self) -> None:
        """Recognize code fence."""
        text = "```python"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.CODE_FENCE
        assert tokens[0].groups[0] == "python"

    def test_multiple_tokens(self) -> None:
        """Extract multiple tokens from text."""
        text = """
▶ [tests] ──→ 3 files
Check `world.auth` for details.
[ ] Fix the bug
📎 Evidence found (moderate)
"""
        tokens = extract_tokens(text)

        assert len(tokens) == 4
        types = [t.token_type for t in tokens]
        assert TokenType.PORTAL_COLLAPSED in types
        assert TokenType.AGENTESE_PATH in types
        assert TokenType.TASK_CHECKBOX in types
        assert TokenType.EVIDENCE_LINK in types

    def test_token_order(self) -> None:
        """Tokens are returned in document order."""
        text = """Line 1: `world.a`
Line 2: `world.b`
Line 3: `world.c`"""
        tokens = extract_tokens(text)

        paths = [t.path for t in tokens]
        assert paths == ["world.a", "world.b", "world.c"]

    def test_token_positions(self) -> None:
        """Tokens have correct position information."""
        text = "Start `world.foo` end"
        tokens = extract_tokens(text)

        assert len(tokens) == 1
        token = tokens[0]
        assert token.line == 0
        assert token.start_col == 6
        assert token.end_col == 17


# === Parse Text Tests ===


class TestParseText:
    """Tests for parse_text() with code block handling."""

    def test_parse_respects_code_blocks(self) -> None:
        """Tokens inside code blocks are excluded (except CODE_FENCE markers)."""
        text = """
Before
```python
`world.in_code` should not match
```
After `world.outside`
"""
        result = parse_text(text)

        # CODE_FENCE tokens are kept (structural markers)
        # AGENTESE path inside code block is excluded
        # AGENTESE path outside code block is kept
        agentese_tokens = [t for t in result.tokens if t.token_type == TokenType.AGENTESE_PATH]

        # Only the outside path
        assert len(agentese_tokens) == 1
        assert agentese_tokens[0].path == "world.outside"

        # The in_code path is NOT present
        all_paths = [t.path for t in result.tokens if t.path]
        assert "world.in_code" not in all_paths

    def test_code_block_tracking(self) -> None:
        """Code blocks are tracked."""
        text = """
```python
def foo():
    pass
```
"""
        result = parse_text(text)

        assert len(result.code_blocks) == 1
        start, end, lang = result.code_blocks[0]
        assert lang == "python"

    def test_parse_with_metadata(self) -> None:
        """Parse text with invisible metadata."""
        metadata = {"source": "world.auth", "copied_at": "2024-01-01"}
        text = encode_invisible_metadata("Hello `world.foo`", metadata)

        result = parse_text(text)

        # Metadata extracted
        assert result.metadata == metadata

        # Text cleaned
        assert METADATA_MARKER not in result.text

        # Tokens still found
        assert len(result.tokens) == 1


# === Invisible Metadata Tests ===


class TestInvisibleMetadata:
    """Tests for invisible metadata encoding/decoding."""

    def test_encode_decode_roundtrip(self) -> None:
        """Encode then decode returns original."""
        original = {"source": "world.auth", "observer": "kent"}
        text = encode_invisible_metadata("Visible text", original)

        visible, metadata = decode_invisible_metadata(text)

        assert visible == "Visible text"
        assert metadata == original

    def test_visible_text_unchanged(self) -> None:
        """Encoded text starts with visible text."""
        text = encode_invisible_metadata("Hello", {"key": "value"})

        # Visible part is first
        assert text.startswith("Hello")

        # Marker separates
        assert METADATA_MARKER in text

    def test_decode_no_metadata(self) -> None:
        """Decode plain text returns None metadata."""
        visible, metadata = decode_invisible_metadata("Plain text")

        assert visible == "Plain text"
        assert metadata is None

    def test_decode_corrupt_metadata(self) -> None:
        """Decode handles corrupt metadata gracefully."""
        # Create text with marker but invalid base64
        text = f"Visible{METADATA_MARKER}not-valid-base64!!!"

        visible, metadata = decode_invisible_metadata(text)

        # Returns original text if decode fails
        assert metadata is None

    def test_metadata_with_datetime(self) -> None:
        """Datetime values are serialized."""
        now = datetime.now()
        original = {"copied_at": now}

        text = encode_invisible_metadata("Text", original)
        _, metadata = decode_invisible_metadata(text)

        # Datetime converted to string
        assert isinstance(metadata["copied_at"], str)

    def test_metadata_survives_copy(self) -> None:
        """Simulated clipboard copy preserves metadata."""
        original = {"source": "world.foo", "observer": "kent"}
        text = encode_invisible_metadata("Copied content", original)

        # Simulate clipboard (just string copy)
        clipboard = text

        # Paste recovers metadata
        visible, metadata = decode_invisible_metadata(clipboard)

        assert metadata == original


# === Convenience Function Tests ===


class TestConvenienceFunctions:
    """Tests for helper functions."""

    def test_is_portal_line_collapsed(self) -> None:
        """Detect collapsed portal line."""
        assert is_portal_line("▶ [tests] ──→ 3 files")
        assert is_portal_line("  ▶ [imports]  ")  # With whitespace

    def test_is_portal_line_expanded(self) -> None:
        """Detect expanded portal line."""
        assert is_portal_line("▼ [tests]")
        assert is_portal_line("  ▼ [implements] spec.md")

    def test_is_portal_line_false(self) -> None:
        """Non-portal lines return False."""
        assert not is_portal_line("Regular text")
        assert not is_portal_line("> blockquote")
        assert not is_portal_line("* bullet")

    def test_is_agentese_path_valid(self) -> None:
        """Valid AGENTESE paths."""
        assert is_agentese_path("world.foo")
        assert is_agentese_path("world.foo.bar.baz")
        assert is_agentese_path("self.context.manifest")
        assert is_agentese_path("concept.spec.auth")
        assert is_agentese_path("void.entropy")
        assert is_agentese_path("time.traces")

    def test_is_agentese_path_invalid(self) -> None:
        """Invalid AGENTESE paths."""
        assert not is_agentese_path("foo")  # No context
        assert not is_agentese_path("world")  # No path
        assert not is_agentese_path("unknown.foo")  # Bad context
        assert not is_agentese_path("world.foo bar")  # Space

    def test_extract_portal_info_collapsed(self) -> None:
        """Extract info from collapsed portal."""
        result = extract_portal_info("▶ [tests] ──→ 3 files")

        assert result is not None
        is_expanded, edge_type, summary = result
        assert is_expanded is False
        assert edge_type == "tests"
        assert summary == "3 files"

    def test_extract_portal_info_expanded(self) -> None:
        """Extract info from expanded portal."""
        result = extract_portal_info("▼ [implements] auth.md")

        assert result is not None
        is_expanded, edge_type, summary = result
        assert is_expanded is True
        assert edge_type == "implements"

    def test_extract_portal_info_none(self) -> None:
        """Non-portal line returns None."""
        assert extract_portal_info("Regular text") is None


# === Edge Case Tests ===


class TestEdgeCases:
    """Tests for edge cases and robustness."""

    def test_empty_text(self) -> None:
        """Handle empty text."""
        tokens = extract_tokens("")
        assert tokens == []

        result = parse_text("")
        assert result.tokens == []

    def test_unicode_content(self) -> None:
        """Handle unicode in text."""
        text = "Check `world.日本語` for details"
        # Should not crash, may or may not match depending on pattern
        tokens = extract_tokens(text)
        # The pattern requires \w+ which may not match Japanese
        # This is expected behavior

    def test_nested_backticks(self) -> None:
        """Handle nested backticks."""
        text = "Use ``world.foo`` not `world.bar`"
        tokens = extract_tokens(text)

        # Should find world.bar but not world.foo (double backticks)
        paths = [t.path for t in tokens if t.path]
        assert "world.bar" in paths

    def test_multiple_portals_same_line(self) -> None:
        """Multiple portals on same line (unlikely but handled)."""
        text = "▶ [a] x ▶ [b] y"
        tokens = extract_tokens(text)

        # Both should be found
        assert len(tokens) == 2
        edges = [t.edge_type for t in tokens]
        assert "a" in edges
        assert "b" in edges

    def test_long_text(self) -> None:
        """Handle long text efficiently."""
        lines = [f"Line with `world.path{i}` content" for i in range(1000)]
        text = "\n".join(lines)

        tokens = extract_tokens(text)

        # Should find all tokens
        assert len(tokens) == 1000
