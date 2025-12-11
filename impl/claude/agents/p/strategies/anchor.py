"""
Anchor-Based Parser (Strategy 4.2)

The Principle: Don't parse the whole structure. Find ANCHORS (known markers)
and extract content between them.

Benefits:
- Structure-independent: Doesn't care about JSON/XML validity
- Ignores filler text: Skips "Sure, here you go" preambles
- Simple implementation: Just string splitting
- High confidence: Anchors are unambiguous markers

Use Cases:
- B-gent hypothesis extraction: Use ###HYPOTHESIS: anchor
- F-gent intent parsing: Use ###BEHAVIOR:, ###CONSTRAINT: anchors
- L-gent catalog search: Use ###ARTIFACT: anchor for results
"""

from typing import Generic, Iterator, Optional, TypeVar

from agents.p.core import ParserConfig, ParseResult

A = TypeVar("A")


class AnchorBasedParser(Generic[A]):
    """
    Extract content using anchor markers, ignore structure.

    Immune to:
    - Conversational filler ("Sure, here are the items:")
    - Malformed JSON structure
    - Extra markdown/formatting
    """

    def __init__(
        self,
        anchor: str = "###ITEM:",
        extractor: Optional[callable] = None,
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize anchor-based parser.

        Args:
            anchor: Marker string to identify items (default: "###ITEM:")
            extractor: Optional function to transform extracted text to A
                      If None, returns text as-is (str)
            config: Parser configuration
        """
        self.anchor = anchor
        self.extractor = extractor or (lambda x: x)
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[list[A]]:
        """
        Extract items prefixed with anchor, discard everything else.

        Args:
            text: Text to parse

        Returns:
            ParseResult[list[A]] with extracted items

        Example:
            >>> parser = AnchorBasedParser(anchor="###ITEM:")
            >>> response = '''
            ... Sure, here's your list! Let me format it nicely:
            ...
            ... {
            ...   "items": [  // Malformed JSON starts here
            ... ###ITEM: First hypothesis
            ... ###ITEM: Second hypothesis
            ... ###ITEM: Third hypothesis
            ...   ]  // Missing closing brace
            ...
            ... Hope this helps!
            ... '''
            >>> result = parser.parse(response)
            >>> result.value
            ["First hypothesis", "Second hypothesis", "Third hypothesis"]
        """
        # Find all anchor markers
        if self.anchor not in text:
            return ParseResult(
                success=False,
                error=f"No anchors '{self.anchor}' found in text",
                strategy="anchor-based",
            )

        # Split on anchor and skip text before first anchor
        items_raw = text.split(self.anchor)[1:]

        # Take first line after anchor (or until next anchor)
        items_text = [item.split("\n")[0].strip() for item in items_raw]

        # Filter empty items
        items_text = [item for item in items_text if item]

        if not items_text:
            return ParseResult(
                success=False,
                error=f"No content found after anchors '{self.anchor}'",
                strategy="anchor-based",
            )

        # Apply extractor function to convert text to A
        try:
            items = [self.extractor(item) for item in items_text]
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Extractor failed: {e}",
                strategy="anchor-based",
                metadata={"raw_items": items_text},
            )

        return ParseResult(
            success=True,
            value=items,
            confidence=0.9,  # High confidence (structure-independent)
            strategy="anchor-based",
            metadata={
                "anchor": self.anchor,
                "items_count": len(items),
            },
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[list[A]]]:
        """
        Parse token stream incrementally.

        Yields ParseResult whenever a complete item is found.
        """
        buffer = ""
        items = []

        for token in tokens:
            buffer += token

            # Check if we have complete items
            if self.anchor in buffer:
                # Extract complete items
                parts = buffer.split(self.anchor)

                # First part is before any anchor (discard)
                # Last part might be incomplete (keep in buffer)
                complete_parts = parts[1:-1]

                # Process complete items
                for part in complete_parts:
                    item_text = part.split("\n")[0].strip()
                    if item_text:
                        try:
                            item = self.extractor(item_text)
                            items.append(item)
                        except Exception:
                            # Skip malformed items in streaming
                            pass

                # Keep last part in buffer (might be incomplete)
                buffer = self.anchor + parts[-1] if len(parts) > 1 else ""

                # Yield current state
                if items:
                    yield ParseResult(
                        success=True,
                        value=items.copy(),  # Return copy of current items
                        confidence=0.85,  # Slightly lower (streaming)
                        partial=True,
                        strategy="anchor-based-stream",
                        stream_position=len(buffer),
                        metadata={
                            "anchor": self.anchor,
                            "items_count": len(items),
                        },
                    )

        # After stream ends, process any remaining buffer content
        if buffer and self.anchor in buffer:
            parts = buffer.split(self.anchor)
            # Process all parts after first (including last)
            for part in parts[1:]:
                item_text = part.split("\n")[0].strip()
                if item_text:
                    try:
                        item = self.extractor(item_text)
                        items.append(item)
                    except Exception:
                        pass

        # Final yield with complete parse
        if items:
            yield ParseResult(
                success=True,
                value=items,
                confidence=0.9,
                partial=False,
                strategy="anchor-based-stream",
                metadata={
                    "anchor": self.anchor,
                    "items_count": len(items),
                },
            )
        else:
            yield ParseResult(
                success=False,
                error=f"No complete items found with anchor '{self.anchor}'",
                strategy="anchor-based-stream",
            )

    def configure(self, **config) -> "AnchorBasedParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return AnchorBasedParser(
            anchor=self.anchor,
            extractor=self.extractor,
            config=new_config,
        )


# Convenience constructors for common use cases


def hypothesis_parser(config: Optional[ParserConfig] = None) -> AnchorBasedParser[str]:
    """
    Create anchor-based parser for B-gent hypotheses.

    Anchor: ###HYPOTHESIS:
    """
    return AnchorBasedParser(
        anchor="###HYPOTHESIS:",
        extractor=lambda x: x.strip(),
        config=config,
    )


def behavior_parser(config: Optional[ParserConfig] = None) -> AnchorBasedParser[str]:
    """
    Create anchor-based parser for F-gent behaviors.

    Anchor: ###BEHAVIOR:
    """
    return AnchorBasedParser(
        anchor="###BEHAVIOR:",
        extractor=lambda x: x.strip(),
        config=config,
    )


def constraint_parser(config: Optional[ParserConfig] = None) -> AnchorBasedParser[str]:
    """
    Create anchor-based parser for F-gent constraints.

    Anchor: ###CONSTRAINT:
    """
    return AnchorBasedParser(
        anchor="###CONSTRAINT:",
        extractor=lambda x: x.strip(),
        config=config,
    )
