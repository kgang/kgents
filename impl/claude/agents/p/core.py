"""
P-gents Core Types

Defines the fundamental types for parsing LLM outputs:
- ParseResult[A]: Transparent parsing result with confidence scoring
- Parser[A]: Protocol for composable parsing strategies
- ParserConfig: Configuration for parser behavior
"""

from dataclasses import dataclass, field
from typing import Any, Generic, Iterator, Optional, Protocol, TypeVar

A = TypeVar("A")


@dataclass
class ParseResult(Generic[A]):
    """
    Result of parsing operation with full transparency.

    Unlike traditional parsers that return success/exception,
    P-gents return ParseResult with:
    - Confidence scoring (0.0-1.0)
    - Partial parse support
    - Repair transparency
    - Stream position tracking
    - Strategy metadata

    Invariants:
    - success=True implies value is not None
    - success=True implies confidence > 0.0
    - success=False implies error is not None
    - partial=True implies confidence < 1.0
    - repairs non-empty implies confidence penalty applied
    """

    success: bool
    value: Optional[A] = None
    strategy: Optional[str] = None  # Which strategy succeeded
    confidence: float = 0.0  # 0.0-1.0
    error: Optional[str] = None  # What went wrong
    partial: bool = False  # Is this a partial parse?
    repairs: list[str] = field(
        default_factory=list
    )  # Applied repairs (ethical transparency)
    stream_position: Optional[int] = None  # For incremental parsing
    metadata: dict[str, Any] = field(default_factory=dict)  # Strategy-specific info

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.success and self.value is None:
            raise ValueError("ParseResult: success=True requires value is not None")
        if self.success and self.confidence <= 0.0:
            raise ValueError("ParseResult: success=True requires confidence > 0.0")
        if not self.success and self.error is None:
            raise ValueError("ParseResult: success=False requires error is not None")
        if self.partial and self.confidence >= 1.0:
            raise ValueError("ParseResult: partial=True requires confidence < 1.0")


class Parser(Protocol[A]):
    """
    Parser transforms fuzzy text into structured data.

    Unlike traditional parsers, P-gents:
    - Accept ANY text (no syntax errors, only parse failures)
    - Return confidence scores (quantify uncertainty)
    - Support partial parsing (degrade gracefully)
    - Support streaming (heterarchical: autonomous mode)
    - Compose via fallback/fusion/switch

    Categorical Structure:
    - Objects: Types A, B, C, ...
    - Morphisms: Parser[A] is a morphism Text → ParseResult[A]
    - Identity: IdentityParser (returns text as-is, confidence=1.0)
    - Composition: See composition patterns (FallbackParser, FusionParser, SwitchParser)
    """

    def parse(self, text: str) -> ParseResult[A]:
        """
        Parse complete text into structured data.

        Args:
            text: The text to parse

        Returns:
            ParseResult[A] with success/failure, confidence, and metadata

        Note:
            This method NEVER raises exceptions on malformed input.
            Instead, returns ParseResult with success=False.
        """
        ...

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """
        Parse token stream incrementally (optional, for streaming).

        Args:
            tokens: Iterator of token strings

        Yields:
            ParseResult[A] for each incremental parse state

        Note:
            Heterarchical principle: Parsers can operate autonomously (streaming)
            or be invoked functionally (single parse).
        """
        ...

    def configure(self, **config: Any) -> "Parser[A]":
        """
        Return new parser with updated configuration.

        Args:
            **config: Configuration parameters

        Returns:
            New Parser[A] instance with updated config

        Note:
            Configuration should tune behavior, not replace design.
            See ParserConfig for valid configuration parameters.
        """
        ...


@dataclass
class ParserConfig:
    """
    Configuration for parser behavior.

    Philosophy: Configuration should TUNE behavior, not replace design.

    Good configuration: Behavioral tuning
    - min_confidence: Reject low-confidence parses
    - allow_partial: Accept partial parses
    - max_attempts: Limit search iterations

    Bad configuration: Structural
    - strategies: list[str] (strategies should be composed, not configured)
    - custom_regex: str (regex should be in strategy)
    - output_format: str (output type should be in Parser[A])
    """

    min_confidence: float = 0.5  # Reject low-confidence parses
    allow_partial: bool = True  # Accept partial parses
    max_attempts: int = 1000  # Limit search iterations
    enable_repair: bool = True  # Try repair strategies
    timeout_ms: int = 5000  # Parsing timeout
    stream_chunk_size: int = 128  # Tokens per stream chunk
    enable_reflection: bool = True  # Use LLM-based error correction
    max_reflection_retries: int = 3  # Reflection loop limit

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError(
                f"min_confidence must be in [0.0, 1.0], got {self.min_confidence}"
            )
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {self.max_attempts}")
        if self.timeout_ms < 0:
            raise ValueError(f"timeout_ms must be >= 0, got {self.timeout_ms}")
        if self.stream_chunk_size < 1:
            raise ValueError(
                f"stream_chunk_size must be >= 1, got {self.stream_chunk_size}"
            )
        if self.max_reflection_retries < 0:
            raise ValueError(
                f"max_reflection_retries must be >= 0, got {self.max_reflection_retries}"
            )


class IdentityParser(Generic[A]):
    """
    Identity parser for the category of parsers.

    Categorical law: Id >> f ≡ f ≡ f >> Id
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[str]:
        """Return text as-is with confidence=1.0."""
        return ParseResult(
            success=True,
            value=text,
            strategy="identity",
            confidence=1.0,
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        """Stream tokens as-is."""
        for token in tokens:
            yield ParseResult(
                success=True,
                value=token,
                strategy="identity",
                confidence=0.99,  # Slightly less than 1.0 for streaming (partial)
                partial=True,
            )

    def configure(self, **config: Any) -> "IdentityParser[A]":
        """Return new IdentityParser with updated config."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()
        return IdentityParser(config=new_config)
