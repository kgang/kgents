"""
Incremental Parser (Strategy 2.3)

The Principle: Build AST incrementally as tokens arrive, mark nodes as
"incomplete" until closing tokens arrive.

Benefits:
- Progressive rendering (W-gent can render partial data immediately)
- Early validation (catch errors before full generation completes)
- Confidence tracking (per-node uncertainty)
- Graceful degradation (partial results are valid)

Use Cases:
- W-gent: Render partial visualizations as data arrives
- E-gent code generation: Highlight complete functions while others generate
- B-gent hypothesis streaming: Show hypotheses as they're generated
"""

import json
from dataclasses import dataclass, field
from typing import Any, Iterator, Literal, Optional

from agents.p.core import ParserConfig, ParseResult


@dataclass
class IncrementalNode:
    """
    AST node with completion status.

    Unlike traditional AST nodes, IncrementalNodes track:
    - Completion status (complete/incomplete)
    - Confidence score (uncertainty about value)
    - Type information (for validation)
    """

    type: Literal[
        "root", "object", "array", "string", "number", "boolean", "null", "incomplete"
    ]
    value: Any
    complete: bool = False
    confidence: float = 0.5
    children: list["IncrementalNode"] = field(default_factory=list)
    key: Optional[str] = None  # For object properties

    def to_dict(self) -> dict:
        """Convert to plain dict for serialization."""
        result = {
            "type": self.type,
            "value": self.value,
            "complete": self.complete,
            "confidence": self.confidence,
        }
        if self.key:
            result["key"] = self.key
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


class IncrementalParser:
    """
    Build JSON AST incrementally as tokens arrive.

    Strategy:
    1. Try to parse complete JSON (fast path)
    2. If incomplete, build partial AST from buffer
    3. Mark nodes as complete/incomplete
    4. Assign confidence based on completeness
    5. Yield incremental results
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        """
        Initialize incremental parser.

        Args:
            config: Parser configuration
        """
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[IncrementalNode]:
        """
        Parse complete text into incremental AST.

        Args:
            text: Text to parse

        Returns:
            ParseResult with IncrementalNode root

        Note:
            If input is complete JSON, all nodes marked complete (confidence=1.0)
            If input is partial, incomplete nodes marked (confidence < 1.0)
        """
        # Try fast path: complete JSON parse
        try:
            data = json.loads(text)
            root = self._build_complete_ast(data)
            return ParseResult(
                success=True,
                value=root,
                confidence=1.0,
                strategy="incremental-complete",
                metadata={"complete": True, "node_count": self._count_nodes(root)},
            )
        except json.JSONDecodeError as e:
            # Slow path: partial parse
            partial_ast = self._parse_partial(text)

            # Calculate overall confidence (min of all node confidences)
            min_confidence = self._min_confidence(partial_ast)

            return ParseResult(
                success=True,
                value=partial_ast,
                confidence=min_confidence,
                partial=True,
                strategy="incremental-partial",
                repairs=["Built partial AST from incomplete JSON"],
                metadata={
                    "complete": False,
                    "parse_error": str(e),
                    "node_count": self._count_nodes(partial_ast),
                    "incomplete_nodes": self._count_incomplete(partial_ast),
                },
            )

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[ParseResult[IncrementalNode]]:
        """
        Parse token stream incrementally.

        Yields ParseResult with current AST state after each token batch.
        Perfect for progressive rendering in W-gent.

        Args:
            tokens: Iterator of text chunks

        Yields:
            ParseResult[IncrementalNode] for each chunk
        """
        buffer = ""

        for token in tokens:
            buffer += token

            # Try to parse current buffer
            try:
                # Complete parse
                data = json.loads(buffer)
                root = self._build_complete_ast(data)
                yield ParseResult(
                    success=True,
                    value=root,
                    confidence=1.0,
                    partial=False,
                    strategy="incremental-stream-complete",
                    stream_position=len(buffer),
                    metadata={"complete": True, "node_count": self._count_nodes(root)},
                )
                return  # Stream complete
            except json.JSONDecodeError:
                # Build partial AST
                partial_ast = self._parse_partial(buffer)
                min_confidence = self._min_confidence(partial_ast)

                yield ParseResult(
                    success=True,
                    value=partial_ast,
                    confidence=min_confidence,
                    partial=True,
                    strategy="incremental-stream-partial",
                    stream_position=len(buffer),
                    repairs=[
                        f"Built partial AST ({self._count_incomplete(partial_ast)} incomplete nodes)"
                    ],
                    metadata={
                        "complete": False,
                        "node_count": self._count_nodes(partial_ast),
                        "incomplete_nodes": self._count_incomplete(partial_ast),
                    },
                )

    def _build_complete_ast(
        self, data: Any, key: Optional[str] = None
    ) -> IncrementalNode:
        """Build AST from successfully parsed JSON data."""
        if isinstance(data, dict):
            children = [self._build_complete_ast(v, k) for k, v in data.items()]
            return IncrementalNode(
                type="object",
                value=data,
                complete=True,
                confidence=1.0,
                children=children,
                key=key,
            )
        elif isinstance(data, list):
            children = [self._build_complete_ast(item, None) for item in data]
            return IncrementalNode(
                type="array",
                value=data,
                complete=True,
                confidence=1.0,
                children=children,
                key=key,
            )
        elif isinstance(data, str):
            return IncrementalNode(
                type="string",
                value=data,
                complete=True,
                confidence=1.0,
                key=key,
            )
        elif isinstance(data, bool):
            return IncrementalNode(
                type="boolean",
                value=data,
                complete=True,
                confidence=1.0,
                key=key,
            )
        elif isinstance(data, (int, float)):
            return IncrementalNode(
                type="number",
                value=data,
                complete=True,
                confidence=1.0,
                key=key,
            )
        elif data is None:
            return IncrementalNode(
                type="null",
                value=None,
                complete=True,
                confidence=1.0,
                key=key,
            )
        else:
            # Fallback for unknown types
            return IncrementalNode(
                type="incomplete",
                value=str(data),
                complete=False,
                confidence=0.3,
                key=key,
            )

    def _parse_partial(self, text: str) -> IncrementalNode:
        """
        Build partial AST from incomplete JSON.

        Uses heuristics to identify structure even when incomplete.
        """
        text = text.strip()

        if not text:
            return IncrementalNode(
                type="incomplete",
                value="",
                complete=False,
                confidence=0.1,  # Minimum non-zero confidence for empty input
            )

        # Try to identify type from opening character
        if text.startswith("{"):
            return self._parse_partial_object(text)
        elif text.startswith("["):
            return self._parse_partial_array(text)
        elif text.startswith('"'):
            return self._parse_partial_string(text)
        elif text[0].isdigit() or text[0] in "+-":
            return self._parse_partial_number(text)
        elif text.startswith("true") or text.startswith("false"):
            return self._parse_partial_boolean(text)
        elif text.startswith("null"):
            return IncrementalNode(
                type="null",
                value=None,
                complete=len(text) >= 4,
                confidence=1.0 if len(text) >= 4 else 0.75,
            )
        else:
            # Unknown/incomplete
            return IncrementalNode(
                type="incomplete",
                value=text,
                complete=False,
                confidence=0.2,
            )

    def _parse_partial_object(self, text: str) -> IncrementalNode:
        """Parse partial object (may be unclosed)."""
        # Try to extract complete key-value pairs
        children = []

        # Simple heuristic: look for "key": value patterns
        import re

        # Find all complete key-value pairs
        kv_pattern = r'"([^"]+)"\s*:\s*([^,}\]]+)'
        matches = re.findall(kv_pattern, text)

        for key, value_str in matches:
            value_str = value_str.strip()

            # Try to parse value
            try:
                if value_str.startswith('"'):
                    # String value
                    value = value_str.strip('"')
                    child = IncrementalNode(
                        type="string",
                        value=value,
                        complete=value_str.endswith('"'),
                        confidence=0.9 if value_str.endswith('"') else 0.6,
                        key=key,
                    )
                elif value_str.startswith("{"):
                    # Nested object
                    child = self._parse_partial_object(value_str)
                    child.key = key
                elif value_str.startswith("["):
                    # Array
                    child = self._parse_partial_array(value_str)
                    child.key = key
                else:
                    # Number, boolean, or incomplete
                    child = IncrementalNode(
                        type="incomplete",
                        value=value_str,
                        complete=False,
                        confidence=0.4,
                        key=key,
                    )

                children.append(child)
            except Exception:
                # Skip malformed values
                pass

        # Check if object is closed
        is_closed = text.rstrip().endswith("}")

        return IncrementalNode(
            type="object",
            value={},  # Placeholder (don't reconstruct dict)
            complete=is_closed,
            confidence=0.8 if is_closed else 0.5,
            children=children,
        )

    def _parse_partial_array(self, text: str) -> IncrementalNode:
        """Parse partial array (may be unclosed)."""
        children = []

        # Simple heuristic: split by commas (naive, but works for simple cases)
        # Skip opening bracket
        content = text[1:].strip()

        # Remove closing bracket if present
        is_closed = content.endswith("]")
        if is_closed:
            content = content[:-1].strip()

        # Try to split items (this is a simplification)
        items = []
        if content:
            # Very naive split (doesn't handle nested structures properly)
            # In a production parser, you'd use a proper tokenizer
            items = [item.strip() for item in content.split(",") if item.strip()]

        for item in items:
            child = self._parse_partial(item)
            children.append(child)

        return IncrementalNode(
            type="array",
            value=[],  # Placeholder
            complete=is_closed,
            confidence=0.8 if is_closed else 0.5,
            children=children,
        )

    def _parse_partial_string(self, text: str) -> IncrementalNode:
        """Parse partial string (may be unclosed)."""
        is_closed = len(text) > 1 and text.count('"') >= 2
        value = text.strip('"')

        return IncrementalNode(
            type="string",
            value=value,
            complete=is_closed,
            confidence=0.9 if is_closed else 0.6,
        )

    def _parse_partial_number(self, text: str) -> IncrementalNode:
        """Parse partial number."""
        try:
            if "." in text or "e" in text.lower():
                value = float(text)
            else:
                value = int(text)

            return IncrementalNode(
                type="number",
                value=value,
                complete=True,
                confidence=0.9,
            )
        except ValueError:
            # Incomplete number
            return IncrementalNode(
                type="incomplete",
                value=text,
                complete=False,
                confidence=0.4,
            )

    def _parse_partial_boolean(self, text: str) -> IncrementalNode:
        """Parse partial boolean."""
        if text == "true":
            return IncrementalNode(
                type="boolean",
                value=True,
                complete=True,
                confidence=1.0,
            )
        elif text == "false":
            return IncrementalNode(
                type="boolean",
                value=False,
                complete=True,
                confidence=1.0,
            )
        else:
            # Incomplete boolean (e.g., "tru" or "fal")
            return IncrementalNode(
                type="incomplete",
                value=text,
                complete=False,
                confidence=0.5,
            )

    def _count_nodes(self, node: IncrementalNode) -> int:
        """Count total nodes in AST."""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def _count_incomplete(self, node: IncrementalNode) -> int:
        """Count incomplete nodes in AST."""
        count = 0 if node.complete else 1
        for child in node.children:
            count += self._count_incomplete(child)
        return count

    def _min_confidence(self, node: IncrementalNode) -> float:
        """Get minimum confidence across all nodes."""
        min_conf = node.confidence
        for child in node.children:
            child_min = self._min_confidence(child)
            min_conf = min(min_conf, child_min)
        return min_conf

    def configure(self, **config) -> "IncrementalParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return IncrementalParser(config=new_config)


# Convenience constructor


def incremental_json_parser(config: Optional[ParserConfig] = None) -> IncrementalParser:
    """
    Create incremental JSON parser for streaming (W-gent, E-gent).

    Builds AST progressively as tokens arrive, enabling:
    - Progressive rendering (show partial results immediately)
    - Early validation (catch errors before completion)
    - Confidence tracking (per-node uncertainty)
    """
    return IncrementalParser(config=config)
