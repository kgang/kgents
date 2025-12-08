"""
Robust multi-strategy parser for LLM-generated code.

This package provides multiple fallback strategies to extract code and metadata
from LLM responses, handling malformed markdown, incomplete code blocks, and
various output formats.

Strategy priority:
1. Structured markdown (## METADATA / ## CODE blocks)
2. JSON + code block extraction
3. Pure code block (```python ... ```)
4. AST-based extraction (find valid Python spans)
5. Repair truncated code

## Package Structure

- `strategies.py` - Individual parsing strategy implementations
- `extractors.py` - Code and metadata extraction utilities
- `repair.py` - Code repair for truncated/incomplete output

## Public API

Core types:
- `ParseStrategy` - Enum of strategy types
- `ParseResult` - Result container with code, metadata, confidence
- `ParserConfig` - Configuration for parser behavior
- `CodeParser` - Main parser orchestrator

Strategy classes:
- `StructuredStrategy` - Parse ## METADATA / ## CODE format
- `JsonCodeStrategy` - Parse JSON + code blocks
- `CodeBlockStrategy` - Parse pure code blocks
- `AstSpanStrategy` - Extract via AST analysis
- `RepairStrategy` - Repair and parse truncated code

Factory:
- `code_parser(config)` - Create CodeParser instance
"""

from __future__ import annotations

from typing import Any, Optional

from .extractors import infer_metadata_from_ast
from .strategies import (
    AstSpanStrategy,
    CodeBlockStrategy,
    JsonCodeStrategy,
    RepairStrategy,
    StructuredStrategy,
)
from .types import ParseResult, ParseStrategy, ParserConfig


class CodeParser:
    """
    Robust parser with multiple fallback strategies.

    Attempts to extract code and metadata from LLM responses using
    progressively more lenient strategies until successful.
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        """Initialize parser with optional configuration."""
        self.config = config or ParserConfig()

        # Initialize strategies
        self._structured = StructuredStrategy(self.config)
        self._json_code = JsonCodeStrategy(self.config)
        self._code_block = CodeBlockStrategy(self.config)
        self._ast_span = AstSpanStrategy(self.config)
        self._repair = RepairStrategy(self.config)

    def parse(self, llm_response: str) -> ParseResult:
        """
        Parse LLM response with fallback strategies.

        Tries strategies in order of preference:
        1. Structured markdown
        2. JSON + code blocks
        3. Pure code block
        4. AST-based extraction
        5. Repair + retry (if enabled)

        Returns the first successful parse result.
        """
        # Strategy 1: Structured markdown
        result = self._structured.parse(llm_response)
        if result.success:
            return result

        # Strategy 2: JSON + code blocks
        result = self._json_code.parse(llm_response)
        if result.success:
            return result

        # Strategy 3: Pure code block
        result = self._code_block.parse(llm_response)
        if result.success:
            return result

        # Strategy 4: AST-based extraction
        result = self._ast_span.parse(llm_response)
        if result.success:
            return result

        # Strategy 5: Try repair if enabled
        if self.config.try_repair:
            result = self._repair.parse(llm_response)
            if result.success:
                return result

        # All strategies failed
        return ParseResult(
            success=False,
            strategy=ParseStrategy.FAILED,
            error="All parsing strategies failed - no valid code found"
        )

    # Expose assessment methods for backward compatibility
    def _assess_completeness(self, code: str) -> float:
        """Assess completeness of extracted code."""
        return self._structured._assess_completeness(code)

    def _infer_metadata_from_ast(self, code: str) -> dict[str, Any]:
        """Infer metadata from code AST when metadata is missing."""
        return infer_metadata_from_ast(code)


# Convenience factory

def code_parser(config: Optional[ParserConfig] = None) -> CodeParser:
    """Create a code parser with optional configuration."""
    return CodeParser(config)


# Public API exports
__all__ = [
    # Core types
    "ParseStrategy",
    "ParseResult",
    "ParserConfig",
    "CodeParser",
    # Strategy classes (for advanced usage)
    "StructuredStrategy",
    "JsonCodeStrategy",
    "CodeBlockStrategy",
    "AstSpanStrategy",
    "RepairStrategy",
    # Factory
    "code_parser",
]
