"""
E-gent Parser Integration with P-gents Protocol

This module provides adapters that make E-gent parsers conform to the
P-gents Parser[A] protocol, enabling composition and standardization.

Architecture:
- Wraps existing E-gent strategies (StructuredStrategy, CodeBlockStrategy, etc.)
- Returns P-gents ParseResult[CodeModule] instead of E-gent ParseResult
- Enables composition via P-gents patterns (FallbackParser, FusionParser)
- Maintains backward compatibility with existing E-gent code
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

from agents.p.core import (
    ParseResult as PParseResult,
    Parser,
    ParserConfig as PParserConfig,
)
from .strategies import (
    StructuredStrategy,
    JsonCodeStrategy,
    CodeBlockStrategy,
    AstSpanStrategy,
    RepairStrategy,
)
from .types import ParserConfig as EParserConfig, ParseResult as EParseResult


@dataclass
class CodeModule:
    """
    Structured code module extracted from LLM response.

    This is the 'A' in Parser[A] for E-gent code parsers.
    """

    code: str
    metadata: dict[str, any]
    description: Optional[str] = None

    def __str__(self) -> str:
        lines = [f"# {self.description}" if self.description else "# Code Module"]
        if self.metadata:
            lines.append(f"# Metadata: {self.metadata}")
        lines.append("")
        lines.append(self.code)
        return "\n".join(lines)


class EgentParserAdapter:
    """
    Adapter that makes E-gent parsing strategies conform to P-gents Parser[CodeModule].

    Bridges:
    - E-gent ParseResult → P-gents ParseResult[CodeModule]
    - E-gent ParserConfig → P-gents ParserConfig
    - E-gent strategy pattern → P-gents Parser protocol

    Example:
        >>> from agents.e.parser.p_integration import code_parser
        >>> result = code_parser.parse(llm_response)
        >>> if result.success:
        ...     print(f"Parsed code with {result.confidence:.0%} confidence")
        ...     print(result.value.code)
    """

    def __init__(
        self,
        strategy: StructuredStrategy
        | JsonCodeStrategy
        | CodeBlockStrategy
        | AstSpanStrategy
        | RepairStrategy,
        config: Optional[PParserConfig] = None,
    ):
        self.strategy = strategy
        self.config = config or PParserConfig()

    def parse(self, text: str) -> PParseResult[CodeModule]:
        """
        Parse LLM response into CodeModule.

        Args:
            text: LLM response text

        Returns:
            PParseResult[CodeModule] with success/failure and confidence
        """
        # Use E-gent strategy
        e_result: EParseResult = self.strategy.parse(text)

        # Convert to P-gents result
        if e_result.success and e_result.code:
            module = CodeModule(
                code=e_result.code,
                metadata=e_result.metadata or {},
                description=e_result.metadata.get("description")
                if e_result.metadata
                else None,
            )

            return PParseResult(
                success=True,
                value=module,
                strategy=f"e-gent:{e_result.strategy.value}",
                confidence=e_result.confidence,
                metadata={
                    "original_strategy": e_result.strategy.value,
                    "e_gent_metadata": e_result.metadata,
                },
            )
        else:
            return PParseResult(
                success=False,
                error=e_result.error or "E-gent parsing failed",
                strategy=f"e-gent:{e_result.strategy.value}",
                confidence=0.0,
            )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[PParseResult[CodeModule]]:
        """
        Stream parsing not yet implemented for E-gent.

        Falls back to accumulating tokens and parsing complete text.
        """
        accumulated = []
        for token in tokens:
            accumulated.append(token)
            # Emit partial results for long streams
            if len(accumulated) % 100 == 0:
                partial_text = "".join(accumulated)
                result = self.parse(partial_text)
                if result.success:
                    yield PParseResult(
                        success=True,
                        value=result.value,
                        strategy=result.strategy,
                        confidence=result.confidence * 0.8,  # Reduce for partial
                        partial=True,
                        metadata=result.metadata,
                    )

        # Final parse
        final_text = "".join(accumulated)
        yield self.parse(final_text)

    def configure(self, **config) -> "EgentParserAdapter":
        """Return new adapter with updated P-gents config."""
        new_config = PParserConfig(**{**vars(self.config), **config})
        new_config.validate()
        return EgentParserAdapter(strategy=self.strategy, config=new_config)


# Convenience factory functions


def structured_code_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """
    Create parser for structured code (## METADATA / ## CODE format).

    Usage:
        >>> parser = structured_code_parser()
        >>> result = parser.parse(response)
    """
    e_config = e_config or EParserConfig()
    return EgentParserAdapter(StructuredStrategy(e_config), p_config)


def json_code_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """Create parser for JSON + code block format."""
    e_config = e_config or EParserConfig()
    return EgentParserAdapter(JsonCodeStrategy(e_config), p_config)


def code_block_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """Create parser for pure code blocks."""
    e_config = e_config or EParserConfig()
    return EgentParserAdapter(CodeBlockStrategy(e_config), p_config)


def ast_span_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """Create parser using AST span extraction (last resort)."""
    e_config = e_config or EParserConfig()
    return EgentParserAdapter(AstSpanStrategy(e_config), p_config)


def repair_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """Create parser with repair strategies for truncated code."""
    e_config = e_config or EParserConfig()
    return EgentParserAdapter(RepairStrategy(e_config), p_config)


def code_parser(
    e_config: Optional[EParserConfig] = None,
    p_config: Optional[PParserConfig] = None,
) -> Parser[CodeModule]:
    """
    Create E-gent's standard fallback code parser.

    Composes strategies in order:
    1. Structured (## METADATA / ## CODE)
    2. JSON + code blocks
    3. Pure code blocks
    4. Repair strategies
    5. AST span extraction

    This is the recommended parser for E-gent code generation.

    Usage:
        >>> from agents.e.parser.p_integration import code_parser
        >>> parser = code_parser()
        >>> result = parser.parse(llm_response)
        >>> if result.success:
        ...     exec(result.value.code, globals())
    """
    from agents.p.composition import FallbackParser

    e_config = e_config or EParserConfig()

    return FallbackParser(
        structured_code_parser(e_config, p_config),
        json_code_parser(e_config, p_config),
        code_block_parser(e_config, p_config),
        repair_parser(e_config, p_config),
        ast_span_parser(e_config, p_config),
    )
