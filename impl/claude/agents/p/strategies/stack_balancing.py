"""
Stack-Balancing Stream Parser (Strategy 2.1)

The Algorithm:
1. Create a Python generator that yields chunks of tokens
2. Maintain a Tag Stack (LIFO) in memory for HTML/XML, Bracket Stack for JSON
3. When stream ends or pauses, virtually append closing delimiters before rendering
4. Keep stream open for more tokens

Benefits:
- Stream HTML/JSON from LLM without breaking the page
- Auto-closes unclosed structures (tags, brackets, braces)
- Progressive rendering (user sees partial results immediately)
- Confidence scoring based on how many auto-closures applied

Use Cases:
- W-gent real-time dashboards: Render partial HTML while LLM streams
- Live JSON API responses: Show progressive results as they arrive
- F-gent prototype streaming: Display code as it's generated
"""

import re
from typing import Any, Iterator, Literal, Optional

from agents.p.core import ParserConfig, ParseResult


class StackBalancingParser:
    """
    Stream parser that auto-closes unclosed structures.

    Supports both HTML/XML (tag-based) and JSON (bracket-based) formats.
    """

    def __init__(
        self,
        mode: Literal["html", "json"] = "json",
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize stack-balancing parser.

        Args:
            mode: "html" for HTML/XML tags, "json" for JSON brackets/braces
            config: Parser configuration
        """
        self.mode = mode
        self.config = config or ParserConfig()

        # Define opener/closer pairs based on mode
        if mode == "html":
            # HTML uses tag matching
            self.tag_pattern = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>")
            self.self_closing_tags = {
                "br",
                "hr",
                "img",
                "input",
                "meta",
                "link",
                "area",
                "base",
                "col",
                "embed",
                "param",
                "source",
                "track",
            }
        elif mode == "json":
            # JSON uses bracket/brace matching
            self.openers = {"{", "["}
            self.closers = {"}", "]"}
            self.pairs = {"{": "}", "[": "]", "}": "{", "]": "["}
        else:
            raise ValueError(f"Unsupported mode: {mode}. Use 'html' or 'json'")

    def parse(self, text: str) -> ParseResult[str]:
        """
        Parse complete text with auto-balancing.

        Args:
            text: Text to parse

        Returns:
            ParseResult[str] with balanced output

        Note:
            If input is already balanced, confidence=1.0
            If auto-closures applied, confidence=0.75-0.9 based on repair count
        """
        if self.mode == "html":
            return self._parse_html(text)
        else:
            return self._parse_json(text)

    def _parse_html(self, text: str) -> ParseResult[str]:
        """Parse HTML with tag balancing."""
        stack: list[str] = []
        repairs: list[str] = []

        # Find all tags
        tags = list(self.tag_pattern.finditer(text))

        for match in tags:
            is_closing = match.group(1) == "/"
            tag_name = match.group(2).lower()

            # Skip self-closing tags
            if tag_name in self.self_closing_tags:
                continue

            if is_closing:
                # Closing tag
                if stack and stack[-1] == tag_name:
                    stack.pop()
                else:
                    # Mismatched closing tag (skip for now)
                    repairs.append(f"Ignored mismatched closing tag: </{tag_name}>")
            else:
                # Opening tag
                stack.append(tag_name)

        # Auto-close remaining tags
        if stack:
            closing_tags = "".join(f"</{tag}>" for tag in reversed(stack))
            balanced_text = text + closing_tags
            repairs.append(f"Auto-closed {len(stack)} unclosed tags: {', '.join(reversed(stack))}")
            confidence = max(0.75, 1.0 - 0.05 * len(stack))
        else:
            balanced_text = text
            confidence = 1.0

        return ParseResult(
            success=True,
            value=balanced_text,
            confidence=confidence,
            strategy="stack-balancing-html",
            repairs=repairs,
            metadata={
                "unclosed_tags": len(stack),
                "tags_in_stack": list(reversed(stack)),
            },
        )

    def _parse_json(self, text: str) -> ParseResult[str]:
        """Parse JSON with bracket/brace balancing."""
        stack = []
        repairs = []

        # Track brackets and braces
        for char in text:
            if char in self.openers:
                stack.append(char)
            elif char in self.closers:
                expected_opener = self.pairs[char]
                if stack and stack[-1] == expected_opener:
                    stack.pop()
                else:
                    # Mismatched closer
                    repairs.append(f"Ignored mismatched closer: {char}")

        # Auto-close remaining openers
        if stack:
            closing_chars = "".join(self.pairs[opener] for opener in reversed(stack))
            balanced_text = text + closing_chars
            repairs.append(f"Auto-closed {len(stack)} unclosed delimiters: {closing_chars}")
            confidence = max(0.75, 1.0 - 0.05 * len(stack))
        else:
            balanced_text = text
            confidence = 1.0

        return ParseResult(
            success=True,
            value=balanced_text,
            confidence=confidence,
            strategy="stack-balancing-json",
            repairs=repairs,
            metadata={
                "unclosed_delimiters": len(stack),
                "stack": [char for char in reversed(stack)],
            },
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        """
        Parse token stream incrementally with auto-balancing.

        Yields ParseResult[str] after each token, with current balanced state.
        Useful for live rendering (W-gent).
        """
        if self.mode == "html":
            yield from self._parse_stream_html(tokens)
        else:
            yield from self._parse_stream_json(tokens)

    def _parse_stream_html(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        """Stream parse HTML with progressive balancing."""
        buffer = ""
        stack: list[str] = []

        for token in tokens:
            buffer += token

            # Update stack based on new token
            tags = list(self.tag_pattern.finditer(token))
            for match in tags:
                is_closing = match.group(1) == "/"
                tag_name = match.group(2).lower()

                if tag_name in self.self_closing_tags:
                    continue

                if is_closing:
                    if stack and stack[-1] == tag_name:
                        stack.pop()
                else:
                    stack.append(tag_name)

            # Create balanced snapshot
            if stack:
                closing_tags = "".join(f"</{tag}>" for tag in reversed(stack))
                balanced = buffer + closing_tags
                confidence = max(0.75, 1.0 - 0.05 * len(stack))
                partial = True
                repairs = [f"Auto-closed {len(stack)} unclosed tags"]
            else:
                balanced = buffer
                confidence = 0.95  # Slightly less than 1.0 for streaming
                partial = len(buffer) > 0
                repairs = []

            yield ParseResult(
                success=True,
                value=balanced,
                confidence=confidence,
                partial=partial,
                strategy="stack-balancing-html-stream",
                stream_position=len(buffer),
                repairs=repairs,
                metadata={
                    "unclosed_tags": len(stack),
                    "tags_in_stack": list(reversed(stack)),
                },
            )

        # Final result
        if stack:
            closing_tags = "".join(f"</{tag}>" for tag in reversed(stack))
            balanced = buffer + closing_tags
            confidence = max(0.75, 1.0 - 0.05 * len(stack))
            repairs = [f"Final auto-closure of {len(stack)} tags: {', '.join(reversed(stack))}"]
        else:
            balanced = buffer
            confidence = 1.0
            repairs = []

        yield ParseResult(
            success=True,
            value=balanced,
            confidence=confidence,
            partial=False,
            strategy="stack-balancing-html-stream",
            repairs=repairs,
            metadata={
                "unclosed_tags": len(stack),
                "final": True,
            },
        )

    def _parse_stream_json(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        """Stream parse JSON with progressive balancing."""
        buffer = ""
        stack = []

        for token in tokens:
            buffer += token

            # Update stack based on new token
            for char in token:
                if char in self.openers:
                    stack.append(char)
                elif char in self.closers:
                    expected_opener = self.pairs[char]
                    if stack and stack[-1] == expected_opener:
                        stack.pop()

            # Create balanced snapshot
            if stack:
                closing_chars = "".join(self.pairs[opener] for opener in reversed(stack))
                balanced = buffer + closing_chars
                confidence = max(0.75, 1.0 - 0.05 * len(stack))
                partial = True
                repairs = [f"Auto-closed {len(stack)} delimiters"]
            else:
                balanced = buffer
                confidence = 0.95
                partial = len(buffer) > 0
                repairs = []

            yield ParseResult(
                success=True,
                value=balanced,
                confidence=confidence,
                partial=partial,
                strategy="stack-balancing-json-stream",
                stream_position=len(buffer),
                repairs=repairs,
                metadata={
                    "unclosed_delimiters": len(stack),
                    "stack": [char for char in reversed(stack)],
                },
            )

        # Final result
        if stack:
            closing_chars = "".join(self.pairs[opener] for opener in reversed(stack))
            balanced = buffer + closing_chars
            confidence = max(0.75, 1.0 - 0.05 * len(stack))
            repairs = [f"Final auto-closure: {closing_chars}"]
        else:
            balanced = buffer
            confidence = 1.0
            repairs = []

        yield ParseResult(
            success=True,
            value=balanced,
            confidence=confidence,
            partial=False,
            strategy="stack-balancing-json-stream",
            repairs=repairs,
            metadata={
                "unclosed_delimiters": len(stack),
                "final": True,
            },
        )

    def configure(self, **config: Any) -> "StackBalancingParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return StackBalancingParser(
            mode=self.mode,
            config=new_config,
        )


# Convenience constructors


def html_stream_parser(config: Optional[ParserConfig] = None) -> StackBalancingParser:
    """
    Create stack-balancing parser for streaming HTML (W-gent).

    Auto-closes unclosed HTML tags for safe rendering.
    """
    return StackBalancingParser(mode="html", config=config)


def json_stream_parser(config: Optional[ParserConfig] = None) -> StackBalancingParser:
    """
    Create stack-balancing parser for streaming JSON.

    Auto-closes unclosed brackets/braces for valid JSON.
    """
    return StackBalancingParser(mode="json", config=config)
