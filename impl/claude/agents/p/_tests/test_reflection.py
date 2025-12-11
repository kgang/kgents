"""
Tests for Reflection Parser (Strategy 3.1)

Tests LLM-based self-repair with reflection loop.
"""

from __future__ import annotations

import json
from typing import Any, Iterator

from agents.p.core import ParserConfig, ParseResult
from agents.p.strategies.reflection import (
    ReflectionContext,
    ReflectionParser,
    create_reflection_parser_with_llm,
    mock_llm_fix_json,
    simple_reflection_prompt,
)


# Simple JSON parser for testing
class SimpleJsonParser:
    """Simple JSON parser for testing reflection."""

    def parse(self, text: str) -> ParseResult[dict[str, Any]]:
        """Parse JSON, return error on failure."""
        try:
            value = json.loads(text)
            return ParseResult(
                success=True,
                value=value,
                confidence=1.0,
                strategy="simple-json",
            )
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error=str(e),
                strategy="simple-json",
            )

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[ParseResult[dict[str, Any]]]:
        """Parse stream (not implemented for testing)."""
        raise NotImplementedError("Stream parsing not needed for tests")

    def configure(self, **config: Any) -> SimpleJsonParser:
        return self


class TestReflectionBasics:
    """Test basic reflection parser functionality."""

    def test_first_try_success_no_reflection(self) -> None:
        """If base parser succeeds first try, no reflection needed."""
        base = SimpleJsonParser()
        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=mock_llm_fix_json,
        )

        result = parser.parse('{"key": "value"}')

        assert result.success
        assert result.value == {"key": "value"}
        assert result.metadata["reflection_attempts"] == 0
        assert not result.metadata["reflection_fixed"]
        assert result.confidence > 0.9  # Minimal penalty

    def test_one_reflection_success(self) -> None:
        """If first try fails, reflect and fix."""
        base = SimpleJsonParser()
        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=mock_llm_fix_json,
            config=ParserConfig(max_reflection_retries=3),
        )

        # Missing closing brace
        result = parser.parse('{"key": "value"')

        assert result.success
        assert result.value == {"key": "value"}
        assert result.metadata["reflection_attempts"] == 1
        assert result.metadata["reflection_fixed"]
        assert len(result.repairs) > 0
        assert "reflection" in result.repairs[0].lower()
        assert result.confidence < 0.9  # Penalty for reflection

    def test_multiple_reflections(self) -> None:
        """Multiple errors require multiple reflections."""
        base = SimpleJsonParser()

        # Track calls
        call_count = [0]

        def counting_fix(text: str, error: str, context: ReflectionContext) -> str:
            call_count[0] += 1
            # Fix incrementally (simulating LLM fixing one issue at a time)
            if call_count[0] == 1:
                # First fix: close brace but leave trailing comma
                return '{"key": "value",}'
            elif call_count[0] == 2:
                # Second fix: remove trailing comma
                return '{"key": "value"}'
            return text

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=counting_fix,
            config=ParserConfig(max_reflection_retries=3),
        )

        result = parser.parse('{"key": "value",')  # Missing brace AND trailing comma

        assert result.success
        assert result.metadata["reflection_attempts"] == 2
        assert call_count[0] == 2

    def test_reflection_exhausted(self) -> None:
        """If max retries exhausted, return failure."""
        base = SimpleJsonParser()

        # LLM that doesn't fix anything
        def bad_fix(text: str, error: str, context: ReflectionContext) -> str:
            return text  # Return unchanged

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=bad_fix,
            config=ParserConfig(max_reflection_retries=2),
        )

        result = parser.parse('{"broken')

        assert not result.success
        assert result.error is not None and "failed after" in result.error.lower()
        assert result.metadata["reflection_attempts"] == 3  # 0, 1, 2 = 3 attempts
        assert len(result.metadata["reflection_errors"]) == 3

    def test_llm_error_handling(self) -> None:
        """If LLM raises exception, return failure."""
        base = SimpleJsonParser()

        def exploding_fix(text: str, error: str, context: ReflectionContext) -> str:
            raise ValueError("LLM API error")

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=exploding_fix,
        )

        result = parser.parse('{"broken')

        assert not result.success
        assert result.error is not None and "llm" in result.error.lower()


class TestConfidenceScoring:
    """Test confidence degradation with retries."""

    def test_confidence_degrades_with_retries(self) -> None:
        """More retries = lower confidence."""
        base = SimpleJsonParser()

        results: list[tuple[int, float]] = []

        for retry_count in [0, 1, 2, 3]:
            # Create parser that succeeds after N retries
            attempt = [0]

            def delayed_fix(text: str, error: str, context: ReflectionContext) -> str:
                attempt[0] += 1
                if attempt[0] == retry_count:
                    return '{"key": "value"}'
                return text  # Not fixed yet

            parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
                base_parser=base,
                llm_fix_fn=delayed_fix,
                config=ParserConfig(max_reflection_retries=5),
            )

            if retry_count == 0:
                result = parser.parse('{"key": "value"}')  # Valid
            else:
                result = parser.parse('{"broken')  # Invalid

            if result.success:
                results.append((retry_count, result.confidence))

        # Confidence should degrade: 0 retries > 1 retry > 2 retries > 3 retries
        confidences = [conf for _, conf in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_zero_retries_high_confidence(self) -> None:
        """Zero retries (first try success) should have high confidence."""
        base = SimpleJsonParser()
        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base, llm_fix_fn=mock_llm_fix_json
        )

        result = parser.parse('{"key": "value"}')

        assert result.success
        assert result.confidence >= 0.9


class TestReflectionContext:
    """Test reflection context tracking."""

    def test_context_tracks_errors(self) -> None:
        """Reflection context should track all previous errors."""
        base = SimpleJsonParser()

        contexts: list[ReflectionContext] = []

        def capturing_fix(text: str, error: str, context: ReflectionContext) -> str:
            # Make a copy to avoid mutation
            contexts.append(
                ReflectionContext(
                    original_input=context.original_input,
                    attempt=context.attempt,
                    previous_errors=list(context.previous_errors),
                    previous_responses=list(context.previous_responses),
                )
            )
            # Fix on second call
            if len(contexts) == 2:
                return '{"key": "value"}'
            return '{"still broken'  # Still broken for first reflection

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=capturing_fix,
            config=ParserConfig(max_reflection_retries=5),
        )

        parser.parse('{"broken')

        # Should have captured at least 2 contexts (2 reflection attempts)
        assert len(contexts) >= 2

        # First context: first reflection attempt
        assert contexts[0].attempt == 0
        assert len(contexts[0].previous_errors) >= 1  # Initial error

        # Second context: second reflection attempt
        assert contexts[1].attempt == 1
        assert len(contexts[1].previous_errors) >= 2  # Accumulated errors

    def test_context_original_input_preserved(self) -> None:
        """Original input should be preserved in context."""
        base = SimpleJsonParser()

        captured_context: list[ReflectionContext] = []

        def capturing_fix(text: str, error: str, context: ReflectionContext) -> str:
            captured_context.append(context)
            return '{"key": "value"}'

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=capturing_fix,
        )

        original = '{"broken'
        parser.parse(original)

        assert captured_context[0].original_input == original


class TestHelperFunctions:
    """Test helper functions."""

    def test_simple_reflection_prompt_format(self) -> None:
        """simple_reflection_prompt should format correctly."""
        context = ReflectionContext(
            original_input='{"test": 1',
            attempt=1,
            previous_errors=["Error 1", "Error 2"],
            previous_responses=[],
        )

        prompt = simple_reflection_prompt(
            text='{"test": 1',
            error="Unclosed brace",
            context=context,
        )

        assert "Unclosed brace" in prompt
        assert '{"test": 1' in prompt
        assert "Error 1" in prompt
        assert "Error 2" in prompt
        assert "Previous attempts (1)" in prompt

    def test_create_reflection_parser_with_llm(self) -> None:
        """create_reflection_parser_with_llm should wire up correctly."""
        base = SimpleJsonParser()

        call_log: list[str] = []

        def mock_llm(prompt: str) -> str:
            call_log.append(prompt)
            return '{"fixed": true}'

        parser: ReflectionParser[dict[str, Any]] = create_reflection_parser_with_llm(
            base_parser=base,
            llm_callable=mock_llm,
        )

        result = parser.parse('{"broken')

        assert result.success
        assert len(call_log) == 1  # LLM called once
        assert "broken" in call_log[0]  # Prompt includes broken input


class TestMockLLMFix:
    """Test mock LLM fixer."""

    def test_mock_fixes_unclosed_brace(self) -> None:
        """Mock LLM should fix unclosed braces."""
        fixed = mock_llm_fix_json(
            '{"key": "value"',
            "Unexpected end of JSON input",
            ReflectionContext("", 0, [], []),
        )

        assert fixed == '{"key": "value"}'

    def test_mock_fixes_unclosed_bracket(self) -> None:
        """Mock LLM should fix unclosed brackets."""
        fixed = mock_llm_fix_json(
            "[1, 2, 3",
            "Unexpected end of JSON input",
            ReflectionContext("", 0, [], []),
        )

        assert fixed == "[1, 2, 3]"

    def test_mock_fixes_trailing_comma(self) -> None:
        """Mock LLM should fix trailing commas."""
        fixed = mock_llm_fix_json(
            '{"key": "value",}',
            "Trailing comma",
            ReflectionContext("", 0, [], []),
        )

        assert fixed == '{"key": "value"}'


class TestConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_instance(self) -> None:
        """configure() should return new parser instance."""
        base = SimpleJsonParser()
        parser1: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base, llm_fix_fn=mock_llm_fix_json
        )
        parser2 = parser1.configure(max_reflection_retries=5)

        assert parser1 is not parser2
        assert (
            parser1.config.max_reflection_retries
            != parser2.config.max_reflection_retries
        )

    def test_max_reflection_retries_respected(self) -> None:
        """Parser should respect max_reflection_retries setting."""
        base = SimpleJsonParser()

        # LLM that never fixes
        def no_fix(text: str, error: str, context: ReflectionContext) -> str:
            return text

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=no_fix,
            config=ParserConfig(max_reflection_retries=1),  # Only 1 retry
        )

        result = parser.parse('{"broken')

        assert not result.success
        # Should try: initial (0), retry1 (1) = 2 attempts total
        assert result.metadata["reflection_attempts"] == 2


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_egent_code_repair(self) -> None:
        """
        E-gent scenario: Generated code has unclosed bracket.
        Reflection fixes it.
        """
        base = SimpleJsonParser()

        # Custom fixer that knows how to fix this specific structure
        def egent_fixer(text: str, error: str, context: ReflectionContext) -> str:
            # E-gent specific fix: close array then object
            if context.attempt == 0:
                return text + "]}"
            return text

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=egent_fixer,
        )

        # Simulate E-gent generating code artifact metadata
        broken_metadata = '{"name": "sort_fn", "type": "function", "lines": [1, 50'

        result = parser.parse(broken_metadata)

        assert result.success
        assert result.value is not None and result.value["name"] == "sort_fn"
        assert result.metadata["reflection_fixed"]

    def test_multiple_error_cascade(self) -> None:
        """
        Multiple errors require cascading reflections.
        """
        base = SimpleJsonParser()

        # Simulate LLM that fixes incrementally
        def incremental_fix(text: str, error: str, context: ReflectionContext) -> str:
            # Simple: just close all open structures
            if text.count("{") > text.count("}"):
                return text + "}"
            if text.count("[") > text.count("]"):
                return text + "]"
            # If already balanced, try removing trailing comma
            return text.rstrip(",")

        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=incremental_fix,
            config=ParserConfig(max_reflection_retries=5),
        )

        # Simple unclosed structure
        result = parser.parse('{"key": "value"')

        assert result.success
        assert result.value is not None and result.value["key"] == "value"
        # Should succeed via reflection
        assert result.metadata["reflection_fixed"]

    def test_confidence_signals_quality(self) -> None:
        """
        Lower confidence after reflection signals lower quality parse.
        User can decide if acceptable.
        """
        base = SimpleJsonParser()
        parser: ReflectionParser[dict[str, Any]] = ReflectionParser(
            base_parser=base,
            llm_fix_fn=mock_llm_fix_json,
        )

        # Perfect input: high confidence
        result1 = parser.parse('{"perfect": true}')

        # Broken input (1 reflection): lower confidence
        result2 = parser.parse('{"broken": true')

        assert result1.success and result2.success
        assert result1.confidence > result2.confidence

        # User can check confidence threshold
        if result2.confidence < 0.8:
            # Maybe ask for human review
            pass
