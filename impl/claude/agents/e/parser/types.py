"""
Core types for the parser package.

Separated to avoid circular import issues.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ParseStrategy(Enum):
    """Strategy used to successfully parse response."""
    STRUCTURED = "structured"  # ## METADATA / ## CODE
    JSON_CODE = "json_code"    # JSON + code blocks
    CODE_BLOCK = "code_block"   # Pure ```python blocks
    AST_SPAN = "ast_span"       # AST-based extraction
    REPAIRED = "repaired"       # Code required syntax repair
    FAILED = "failed"           # All strategies failed


@dataclass
class ParseResult:
    """Result of parsing LLM response."""
    success: bool
    code: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    strategy: ParseStrategy = ParseStrategy.FAILED
    error: Optional[str] = None
    confidence: float = 0.0  # 0.0-1.0, based on completeness checks


@dataclass
class ParserConfig:
    """Configuration for parser behavior."""
    # Minimum lines for "complete" module
    min_module_lines: int = 20
    # Require imports in extracted code
    require_imports: bool = True
    # Require meaningful content (classes/functions)
    require_content: bool = True
    # Maximum attempts for AST span search
    max_ast_attempts: int = 1000
    # Try to repair truncated strings
    try_repair: bool = True
