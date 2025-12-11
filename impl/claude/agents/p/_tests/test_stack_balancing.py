"""
Tests for Stack-Balancing Parser (Strategy 2.1)

Tests both HTML and JSON modes, streaming and non-streaming.
"""

from __future__ import annotations

import pytest
from agents.p.strategies.stack_balancing import (
    StackBalancingParser,
    html_stream_parser,
    json_stream_parser,
)


class TestStackBalancingJSON:
    """Test JSON bracket/brace balancing."""

    def test_balanced_json(self) -> None:
        """Already balanced JSON should have confidence=1.0"""
        parser = StackBalancingParser(mode="json")
        result = parser.parse('{"key": "value"}')

        assert result.success
        assert result.value == '{"key": "value"}'
        assert result.confidence == 1.0
        assert len(result.repairs) == 0

    def test_unclosed_brace(self) -> None:
        """Unclosed brace should auto-close with confidence penalty"""
        parser = StackBalancingParser(mode="json")
        result = parser.parse('{"key": "value"')

        assert result.success
        assert result.value == '{"key": "value"}'
        assert result.confidence < 1.0
        assert result.confidence >= 0.75
        assert len(result.repairs) == 1
        assert "Auto-closed" in result.repairs[0]

    def test_unclosed_bracket(self) -> None:
        """Unclosed bracket should auto-close"""
        parser = StackBalancingParser(mode="json")
        result = parser.parse("[1, 2, 3")

        assert result.success
        assert result.value == "[1, 2, 3]"
        assert result.confidence < 1.0
        assert len(result.repairs) == 1

    def test_nested_unclosed(self) -> None:
        """Multiple unclosed delimiters should all auto-close"""
        parser = StackBalancingParser(mode="json")
        result = parser.parse('{"outer": {"inner": [1, 2')

        assert result.success
        assert result.value == '{"outer": {"inner": [1, 2]}}'
        assert result.confidence < 1.0
        assert result.metadata["unclosed_delimiters"] == 3  # { { [

    def test_mismatched_closer(self) -> None:
        """Mismatched closer should be ignored"""
        parser = StackBalancingParser(mode="json")
        result = parser.parse('{"key": ]')

        assert result.success
        # Should still auto-close the opening brace
        assert result.value == '{"key": ]}'
        assert "mismatched" in result.repairs[0].lower()

    def test_multiple_unclosed_penalty(self) -> None:
        """More unclosed delimiters = lower confidence"""
        parser = StackBalancingParser(mode="json")

        result1 = parser.parse('{"a"')  # 1 unclosed
        result2 = parser.parse('{"a": {"b"')  # 2 unclosed

        assert result1.confidence > result2.confidence


class TestStackBalancingHTML:
    """Test HTML tag balancing."""

    def test_balanced_html(self) -> None:
        """Already balanced HTML should have confidence=1.0"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<div>Hello</div>")

        assert result.success
        assert result.value == "<div>Hello</div>"
        assert result.confidence == 1.0
        assert len(result.repairs) == 0

    def test_unclosed_div(self) -> None:
        """Unclosed div should auto-close"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<div>Hello")

        assert result.success
        assert result.value == "<div>Hello</div>"
        assert result.confidence < 1.0
        assert len(result.repairs) == 1
        assert "div" in result.repairs[0]

    def test_nested_unclosed_tags(self) -> None:
        """Multiple unclosed tags should all auto-close in reverse order"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<div><p><span>Text")

        assert result.success
        assert result.value == "<div><p><span>Text</span></p></div>"
        assert result.metadata["unclosed_tags"] == 3
        # Stack is LIFO: most recent tag first
        assert result.metadata["tags_in_stack"] == ["span", "p", "div"]

    def test_self_closing_tags_ignored(self) -> None:
        """Self-closing tags (br, hr, img) should not be tracked"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<div>Hello<br>World</div>")

        assert result.success
        assert result.value == "<div>Hello<br>World</div>"
        assert result.confidence == 1.0

    def test_img_tag_self_closing(self) -> None:
        """Image tags should be treated as self-closing"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse('<div><img src="test.jpg"><p>Text')

        assert result.success
        assert result.value == '<div><img src="test.jpg"><p>Text</p></div>'
        # Only div and p should be in stack (not img)
        assert result.metadata["unclosed_tags"] == 2

    def test_mismatched_closing_tag(self) -> None:
        """Mismatched closing tag should be ignored"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<div></span>")

        assert result.success
        assert "mismatched" in result.repairs[0].lower()

    def test_case_insensitive_tags(self) -> None:
        """HTML tags should be case-insensitive"""
        parser = StackBalancingParser(mode="html")
        result = parser.parse("<DIV>Text")

        assert result.success
        assert result.value is not None
        assert "</div>" in result.value.lower()


class TestStreamingJSON:
    """Test streaming JSON parsing."""

    def test_stream_builds_progressively(self) -> None:
        """Stream should yield progressive balanced results"""
        parser = StackBalancingParser(mode="json")
        tokens = ["{", '"key"', ":", '"val']

        results = list(parser.parse_stream(iter(tokens)))

        # Should get results for each token
        assert len(results) > 0

        # All intermediate results should be partial
        for result in results[:-1]:
            assert result.partial
            assert result.success

        # Final result should not be partial
        assert not results[-1].partial

    def test_stream_auto_closes_at_each_step(self) -> None:
        """Each streaming step should have balanced output"""
        parser = StackBalancingParser(mode="json")
        tokens = ["{", '"a"', ":", "[", "1"]

        results = list(parser.parse_stream(iter(tokens)))

        # Each result should be balanced (closeable)
        for result in results:
            assert result.success
            # Check that we have auto-closures
            if result.metadata["unclosed_delimiters"] > 0:
                assert len(result.repairs) > 0

    def test_stream_final_complete(self) -> None:
        """Final streaming result should be complete"""
        parser = StackBalancingParser(mode="json")
        tokens = ["{", '"key"', ":", '"value"', "}"]

        results = list(parser.parse_stream(iter(tokens)))

        final = results[-1]
        assert final.success
        assert not final.partial
        assert final.confidence == 1.0  # Fully balanced
        assert final.metadata.get("final")


class TestStreamingHTML:
    """Test streaming HTML parsing."""

    def test_html_stream_progressive_closing(self) -> None:
        """HTML stream should progressively auto-close tags"""
        parser = StackBalancingParser(mode="html")
        tokens = ["<div>", "<p>", "Text"]

        results = list(parser.parse_stream(iter(tokens)))

        assert len(results) > 0

        # Each result should have balanced HTML
        for result in results[:-1]:
            assert result.success
            assert result.partial

    def test_html_stream_opens_and_closes(self) -> None:
        """HTML stream should handle tags opening and closing"""
        parser = StackBalancingParser(mode="html")
        tokens = ["<div>", "Hello", "</div>"]

        results = list(parser.parse_stream(iter(tokens)))

        final = results[-1]
        assert final.success
        assert final.value is not None
        assert "<div>Hello</div>" in final.value
        assert final.confidence == 1.0

    def test_html_stream_unclosed_at_end(self) -> None:
        """HTML stream with unclosed tags at end should auto-close"""
        parser = StackBalancingParser(mode="html")
        tokens = ["<div>", "<p>", "Text"]

        results = list(parser.parse_stream(iter(tokens)))

        final = results[-1]
        assert final.success
        assert final.value is not None
        assert "</p></div>" in final.value
        assert final.metadata["unclosed_tags"] == 2


class TestConvenienceFunctions:
    """Test convenience constructor functions."""

    def test_html_stream_parser(self) -> None:
        """html_stream_parser should create HTML mode parser"""
        parser = html_stream_parser()
        result = parser.parse("<div>Test")

        assert result.success
        assert result.value == "<div>Test</div>"

    def test_json_stream_parser(self) -> None:
        """json_stream_parser should create JSON mode parser"""
        parser = json_stream_parser()
        result = parser.parse('{"key"')

        assert result.success
        assert result.value == '{"key"}'


class TestConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_instance(self) -> None:
        """configure() should return new parser instance"""
        parser1 = StackBalancingParser(mode="json")
        parser2 = parser1.configure(min_confidence=0.8)

        assert parser1 is not parser2
        assert parser1.config.min_confidence != parser2.config.min_confidence

    def test_configure_validation(self) -> None:
        """configure() should validate new configuration"""
        parser = StackBalancingParser(mode="json")

        with pytest.raises(ValueError):
            parser.configure(min_confidence=1.5)  # Out of range

    def test_invalid_mode_raises(self) -> None:
        """Invalid mode should raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported mode"):
            StackBalancingParser(mode="xml")  # type: ignore[arg-type]


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_wgent_streaming_html(self) -> None:
        """
        W-gent scenario: Stream HTML dashboard from LLM.
        LLM generates HTML in chunks, may not close all tags.
        """
        parser = html_stream_parser()

        # Simulate LLM streaming HTML
        chunks = [
            "<html>",
            "<body>",
            '<div class="dashboard">',
            "<h1>Status</h1>",
            '<div class="card">',
            "Agent is running...",
            # LLM stream ends abruptly (no closing tags)
        ]

        results = list(parser.parse_stream(iter(chunks)))

        # All intermediate results should be renderable (balanced)
        for result in results:
            assert result.success
            # Each result should have balanced HTML
            assert result.value is not None
            assert result.value.count("<") >= result.value.count(">")

        # Final result should auto-close all tags
        final = results[-1]
        assert final.value is not None
        assert "</div>" in final.value
        assert "</body>" in final.value
        assert "</html>" in final.value

    def test_json_api_response_streaming(self) -> None:
        """
        Streaming JSON API response that may be incomplete.
        """
        parser = json_stream_parser()

        chunks = [
            "{",
            '"status": "ok",',
            '"data": {',
            '"users": [',
            '{"id": 1',
            # Stream interrupted
        ]

        results = list(parser.parse_stream(iter(chunks)))

        # Each result should be parseable (balanced)
        for result in results:
            assert result.success

        # Final should auto-close everything
        final = results[-1]
        assert final.value is not None
        assert final.value.count("{") == final.value.count("}")
        assert final.value.count("[") == final.value.count("]")

    def test_confidence_degrades_with_repairs(self) -> None:
        """
        More auto-closures = lower confidence.
        User can decide if confidence is acceptable.
        """
        parser = StackBalancingParser(mode="json")

        # 1 unclosed
        result1 = parser.parse('{"a": 1')

        # 3 unclosed
        result2 = parser.parse('{"a": {"b": {"c": 1')

        # 5 unclosed
        result3 = parser.parse('{"a": {"b": {"c": {"d": {"e": 1')

        # Confidence should degrade
        assert result1.confidence > result2.confidence > result3.confidence

        # But all should succeed
        assert result1.success and result2.success and result3.success
