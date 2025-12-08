"""
Robust multi-strategy parser for LLM-generated code.

This module provides multiple fallback strategies to extract code and metadata
from LLM responses, handling malformed markdown, incomplete code blocks, and
various output formats.

Strategy priority:
1. Structured markdown (## METADATA / ## CODE blocks)
2. JSON + code block extraction
3. Pure code block (```python ... ```)
4. AST-based extraction (find valid Python spans)
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
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


def _repair_truncated_strings(code: str) -> tuple[str, list[str]]:
    """
    Attempt to repair truncated triple-quoted strings.

    Common issue: LLM runs out of tokens mid-f-string.
    Returns (repaired_code, list_of_repairs_made).
    """
    repairs: list[str] = []

    # Count open triple quotes
    triple_double = code.count('"""')
    triple_single = code.count("'''")

    # Check for f-strings specifically
    fstring_pattern = r'f"""[^"]*$|f\'\'\'[^\']*$'

    repaired = code

    # If odd number of triple quotes, close them
    if triple_double % 2 == 1:
        # Find the last unclosed one
        last_open = code.rfind('"""')
        if last_open != -1:
            # Check if it's an f-string
            prefix_start = max(0, last_open - 10)
            prefix = code[prefix_start:last_open]
            if 'f' in prefix or 'f"""' in code[last_open-1:last_open+3]:
                # Truncated f-string - close it simply
                repaired = code + '"""'
                repairs.append(f"Closed truncated f-string at char {last_open}")
            else:
                repaired = code + '"""'
                repairs.append(f"Closed truncated triple-double-quote at char {last_open}")

    if triple_single % 2 == 1:
        last_open = repaired.rfind("'''")
        if last_open != -1:
            repaired = repaired + "'''"
            repairs.append(f"Closed truncated triple-single-quote at char {last_open}")

    # Check for unclosed regular strings at end of lines
    lines = repaired.split('\n')
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        # Check for unclosed single quotes
        single_count = stripped.count("'") - stripped.count("\\'") - stripped.count("'''") * 3
        double_count = stripped.count('"') - stripped.count('\\"') - stripped.count('"""') * 3

        # Don't try to repair lines, too error prone

    return repaired, repairs


def _repair_incomplete_function(code: str) -> tuple[str, list[str]]:
    """
    Attempt to repair incomplete function definitions.

    Common issue: Function body is truncated mid-statement.
    """
    repairs: list[str] = []

    lines = code.split('\n')

    # Check if we end mid-function (indented line without proper closure)
    if lines:
        last_line = lines[-1]
        # If last line is indented and doesn't end with : or complete statement
        if last_line and last_line[0] == ' ':
            stripped = last_line.strip()
            # If it looks incomplete (ends with operator, comma, open paren)
            if stripped and stripped[-1] in '(,+-*/:=':
                # Add a pass statement to complete the function
                indent = len(last_line) - len(last_line.lstrip())
                lines.append(' ' * indent + 'pass  # AUTO-REPAIR: truncated')
                repairs.append(f"Added pass to complete truncated function")

    return '\n'.join(lines), repairs


class CodeParser:
    """
    Robust parser with multiple fallback strategies.

    Attempts to extract code and metadata from LLM responses using
    progressively more lenient strategies until successful.
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        """Initialize parser with optional configuration."""
        self.config = config or ParserConfig()

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
        result = self._parse_structured(llm_response)
        if result.success:
            return result

        # Strategy 2: JSON + code blocks
        result = self._parse_json_code(llm_response)
        if result.success:
            return result

        # Strategy 3: Pure code block
        result = self._parse_code_block(llm_response)
        if result.success:
            return result

        # Strategy 4: AST-based extraction
        result = self._parse_ast_spans(llm_response)
        if result.success:
            return result

        # Strategy 5: Try repair if enabled
        if self.config.try_repair:
            result = self._parse_with_repair(llm_response)
            if result.success:
                return result

        # All strategies failed
        return ParseResult(
            success=False,
            strategy=ParseStrategy.FAILED,
            error="All parsing strategies failed - no valid code found"
        )

    def _parse_with_repair(self, response: str) -> ParseResult:
        """
        Try to repair and parse truncated code.

        Applies repairs for common LLM truncation issues:
        - Unclosed triple-quoted strings (f-strings)
        - Incomplete function bodies
        """
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

        # Try repairs
        repaired, string_repairs = _repair_truncated_strings(raw_code)
        repaired, func_repairs = _repair_incomplete_function(repaired)

        all_repairs = string_repairs + func_repairs

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
        json_match = re.search(
            r'```(?:json)?\s*\n(\{.*?\})\s*```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        metadata = None
        if json_match:
            try:
                metadata = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Reduce confidence for repaired code
        confidence = self._assess_completeness(repaired) * 0.8

        return ParseResult(
            success=True,
            code=repaired,
            metadata=metadata or self._infer_metadata_from_ast(repaired),
            strategy=ParseStrategy.REPAIRED,
            confidence=confidence,
            error=f"Repairs applied: {'; '.join(all_repairs)}"
        )

    def _parse_structured(self, response: str) -> ParseResult:
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
        # Extract metadata block
        metadata_match = re.search(
            r'##\s*METADATA.*?```(?:json)?\s*\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        # Extract code block
        code_match = re.search(
            r'##\s*CODE.*?```(?:python)?\s*\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if not code_match:
            return ParseResult(
                success=False,
                error="No ## CODE block found"
            )

        code = code_match.group(1).strip()

        # Validate code syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return ParseResult(
                success=False,
                error=f"Structured parse: code has syntax error at line {e.lineno}: {e.msg}"
            )

        # Parse metadata (optional)
        metadata = None
        if metadata_match:
            try:
                metadata = json.loads(metadata_match.group(1).strip())
            except json.JSONDecodeError as e:
                # Metadata parse failure is not critical
                pass

        # Check completeness
        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=metadata or self._infer_metadata_from_ast(code),
            strategy=ParseStrategy.STRUCTURED,
            confidence=confidence
        )

    def _parse_json_code(self, response: str) -> ParseResult:
        """
        Parse response with separate JSON metadata and code blocks.

        Looks for any JSON object and any Python code block.
        """
        # Find JSON (anywhere)
        json_match = re.search(
            r'```(?:json)?\s*\n(\{.*?\})\s*```',
            response,
            re.DOTALL | re.IGNORECASE
        )

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

        # Parse metadata (optional)
        metadata = None
        if json_match:
            try:
                metadata = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=metadata or self._infer_metadata_from_ast(code),
            strategy=ParseStrategy.JSON_CODE,
            confidence=confidence
        )

    def _parse_code_block(self, response: str) -> ParseResult:
        """
        Parse pure code block without metadata.

        Looks for any ```python block, validates syntax.
        Handles malformed blocks (missing closing fence).
        """
        # Try Python-tagged blocks first (with proper closing)
        patterns = [
            r'```python\s*\n(.*?)```',
            r'```py\s*\n(.*?)```',
            r'```\s*\n(.*?)```',
        ]

        code = None
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                try:
                    ast.parse(candidate)
                    code = candidate
                    break
                except SyntaxError:
                    continue

        # If no valid closed block, try to extract from unclosed blocks
        if not code:
            # Try to find start of code block and take everything after
            unclosed_patterns = [
                r'```python\s*\n(.*)',
                r'```py\s*\n(.*)',
                r'```\s*\n(.*)',
            ]

            for pattern in unclosed_patterns:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    # Clean up potential trailing markdown/text
                    # Look for end of Python code (dedented line or markdown)
                    lines = candidate.split('\n')
                    code_lines = []
                    for line in lines:
                        # Stop if we hit markdown-like syntax
                        if line.strip().startswith('#') and not line.strip().startswith('# '):
                            break
                        code_lines.append(line)

                    candidate = '\n'.join(code_lines).strip()

                    try:
                        ast.parse(candidate)
                        code = candidate
                        break
                    except SyntaxError:
                        continue

        if not code:
            return ParseResult(
                success=False,
                error="No valid Python code block found"
            )

        confidence = self._assess_completeness(code)

        return ParseResult(
            success=True,
            code=code,
            metadata=self._infer_metadata_from_ast(code),
            strategy=ParseStrategy.CODE_BLOCK,
            confidence=confidence
        )

    def _parse_ast_spans(self, response: str) -> ParseResult:
        """
        Extract code by finding valid Python AST spans.

        Tolerates markdown noise, partial responses, etc.
        This is a last-resort strategy that tries to find ANY
        valid Python code in the response.
        """
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
                            metadata=self._infer_metadata_from_ast(code_candidate),
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
                metadata=self._infer_metadata_from_ast(best_code),
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

    def _infer_metadata_from_ast(self, code: str) -> dict[str, Any]:
        """
        Infer metadata from code AST when metadata is missing.

        Extracts:
        - changed_symbols: list of class/function names
        - has_imports: bool
        - line_count: int
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {}

        symbols = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(node.name)

        has_imports = any(
            isinstance(n, (ast.Import, ast.ImportFrom))
            for n in tree.body
        )

        return {
            "changed_symbols": symbols,
            "has_imports": has_imports,
            "line_count": len(code.split('\n')),
            "inferred": True  # Mark as inferred metadata
        }


# Convenience factory

def code_parser(config: Optional[ParserConfig] = None) -> CodeParser:
    """Create a code parser with optional configuration."""
    return CodeParser(config)
