"""
Parsing strategy implementations.

Each strategy class handles a different response format:
- StructuredStrategy: ## METADATA / ## CODE blocks
- JsonCodeStrategy: JSON + code blocks
- CodeBlockStrategy: Pure ```python blocks
- AstSpanStrategy: AST-based extraction
- RepairStrategy: Repair truncated code
"""

from __future__ import annotations

import ast
import re
from typing import Any, Optional

from .extractors import (
    extract_code_block,
    extract_json_metadata,
    extract_structured_blocks,
    infer_metadata_from_ast,
)
from .repair import apply_repairs
from .types import ParseResult, ParseStrategy, ParserConfig


class BaseParsingStrategy:
    """Base class for parsing strategies."""

    def __init__(self, config: ParserConfig):
        self.config = config

    def parse(self, response: str) -> ParseResult:
        """Parse response and return result."""
        raise NotImplementedError

    def _assess_completeness(self, code: str) -> float:
        """
        Assess completeness of extracted code.

        Returns confidence score 0.0-1.0 based on:
        - Has imports
        - Has classes/functions
        - Length
        - No obvious incompleteness markers
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        confidence = 0.5  # Base confidence for valid syntax

        # Check for imports
        has_imports = any(
            isinstance(n, (ast.Import, ast.ImportFrom))
            for n in tree.body
        )
        if has_imports:
            confidence += 0.15

        # Check for content
        has_content = any(
            isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            for n in tree.body
        )
        if has_content:
            confidence += 0.15

        # Check length
        lines = code.split('\n')
        if len(lines) >= self.config.min_module_lines:
            confidence += 0.1

        # Check for incompleteness markers
        incompleteness_markers = ['...', 'pass  # TODO', '# TODO', '# FIXME', 'NotImplemented']
        has_markers = any(marker in code for marker in incompleteness_markers)
        if has_markers:
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))


class StructuredStrategy(BaseParsingStrategy):
    """
    Parse structured response with ## METADATA and ## CODE headers.

    Expected format:
        ## METADATA
        ```json
        {"description": "...", ...}
        ```

        ## CODE
        ```python
        # code here
        ```
    """

    def parse(self, response: str) -> ParseResult:
        code, metadata = extract_structured_blocks(response)

        if not code:
            return ParseResult(
                success=False,
                error="No ## CODE block found"
            )

        # Validate code syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return ParseResult(
                success=False,
                error=f"Structured parse: code has syntax error at line {e.lineno}: {e.msg}"
            )

        # Check completeness
        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=metadata or infer_metadata_from_ast(code),
            strategy=ParseStrategy.STRUCTURED,
            confidence=confidence
        )


class JsonCodeStrategy(BaseParsingStrategy):
    """
    Parse response with separate JSON metadata and code blocks.

    Looks for any JSON object and any Python code block.
    """

    def parse(self, response: str) -> ParseResult:
        # Find JSON (anywhere)
        metadata = extract_json_metadata(response)

        # Find Python code (anywhere)
        code_match = re.search(
            r'```(?:python|py)\s*\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not code_match:
            return ParseResult(
                success=False,
                error="No Python code block found"
            )

        code = code_match.group(1).strip()

        # Validate syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return ParseResult(
                success=False,
                error=f"JSON+code parse: syntax error at line {e.lineno}: {e.msg}"
            )

        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=metadata or infer_metadata_from_ast(code),
            strategy=ParseStrategy.JSON_CODE,
            confidence=confidence
        )


class CodeBlockStrategy(BaseParsingStrategy):
    """
    Parse pure code block without metadata.

    Looks for any ```python block, validates syntax.
    Handles malformed blocks (missing closing fence).
    """

    def parse(self, response: str) -> ParseResult:
        code = extract_code_block(response, allow_unclosed=True)

        if not code:
            return ParseResult(
                success=False,
                error="No valid Python code block found"
            )

        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=infer_metadata_from_ast(code),
            strategy=ParseStrategy.CODE_BLOCK,
            confidence=confidence
        )


class RepairStrategy(BaseParsingStrategy):
    """
    Try to repair and parse truncated code.

    Applies repairs for common LLM truncation issues:
    - Unclosed triple-quoted strings (f-strings)
    - Incomplete function bodies
    """

    def parse(self, response: str) -> ParseResult:
        # Extract code block first (even if invalid)
        code_match = re.search(
            r'```(?:python|py)?\s*\n(.*)',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not code_match:
            return ParseResult(
                success=False,
                error="No code block found to repair"
            )

        raw_code = code_match.group(1)

        # Remove trailing markdown if present
        if '```' in raw_code:
            raw_code = raw_code.split('```')[0]

        raw_code = raw_code.strip()

        # Apply repairs
        repaired, all_repairs = apply_repairs(raw_code)

        if not all_repairs:
            return ParseResult(
                success=False,
                error="No repairs applicable"
            )

        # Try to parse repaired code
        try:
            ast.parse(repaired)
        except SyntaxError as e:
            return ParseResult(
                success=False,
                error=f"Repair failed: syntax error at line {e.lineno}: {e.msg}"
            )

        # Extract metadata from original response
        metadata = extract_json_metadata(response)

        # Reduce confidence for repaired code
        confidence = self._assess_completeness(repaired) * 0.8

        return ParseResult(
            success=True,
            code=repaired,
            metadata=metadata or infer_metadata_from_ast(repaired),
            strategy=ParseStrategy.REPAIRED,
            confidence=confidence,
            error=f"Repairs applied: {'; '.join(all_repairs)}"
        )


class AstSpanStrategy(BaseParsingStrategy):
    """
    Extract code by finding valid Python AST spans.

    Tolerates markdown noise, partial responses, etc.
    This is a last-resort strategy that tries to find ANY
    valid Python code in the response.
    """

    def parse(self, response: str) -> ParseResult:
        lines = response.split('\n')

        # Try progressively larger spans
        best_code = None
        best_score = 0

        attempts = 0
        for start in range(len(lines)):
            for end in range(start + self.config.min_module_lines, len(lines) + 1):
                if attempts >= self.config.max_ast_attempts:
                    break

                attempts += 1
                code_candidate = '\n'.join(lines[start:end])

                try:
                    tree = ast.parse(code_candidate)

                    # Score this candidate
                    score = self._score_ast_tree(tree)

                    if score > best_score:
                        best_code = code_candidate
                        best_score = score

                    # If we found a "complete" module, stop searching
                    if self._is_complete_module(tree):
                        return ParseResult(
                            success=True,
                            code=code_candidate,
                            metadata=infer_metadata_from_ast(code_candidate),
                            strategy=ParseStrategy.AST_SPAN,
                            confidence=self._assess_completeness(code_candidate)
                        )

                except SyntaxError:
                    continue

            if attempts >= self.config.max_ast_attempts:
                break

        # Return best partial match if found
        if best_code and best_score > 0:
            return ParseResult(
                success=True,
                code=best_code,
                metadata=infer_metadata_from_ast(best_code),
                strategy=ParseStrategy.AST_SPAN,
                confidence=self._assess_completeness(best_code)
            )

        return ParseResult(
            success=False,
            error=f"No valid AST spans found after {attempts} attempts"
        )

    def _is_complete_module(self, tree: ast.Module) -> bool:
        """
        Check if AST represents a complete module.

        A complete module should have:
        - Imports (if configured)
        - Meaningful content (classes or functions, if configured)
        - Substantial length (>= min_module_lines)
        """
        # Check for imports
        has_imports = any(
            isinstance(n, (ast.Import, ast.ImportFrom))
            for n in tree.body
        )

        # Check for meaningful content
        has_content = any(
            isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            for n in tree.body
        )

        # Check length
        source_lines = ast.unparse(tree).split('\n')
        is_substantial = len(source_lines) >= self.config.min_module_lines

        # Apply configuration rules
        if self.config.require_imports and not has_imports:
            return False

        if self.config.require_content and not has_content:
            return False

        return is_substantial

    def _score_ast_tree(self, tree: ast.Module) -> int:
        """
        Score an AST tree for completeness.

        Higher scores indicate more complete/desirable modules.
        """
        score = 0

        # Count imports
        imports = sum(
            1 for n in tree.body
            if isinstance(n, (ast.Import, ast.ImportFrom))
        )
        score += imports * 2

        # Count classes
        classes = sum(
            1 for n in tree.body
            if isinstance(n, ast.ClassDef)
        )
        score += classes * 10

        # Count functions
        functions = sum(
            1 for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        score += functions * 5

        # Penalize very short modules
        source_lines = ast.unparse(tree).split('\n')
        if len(source_lines) < self.config.min_module_lines:
            score -= 20

        return score
