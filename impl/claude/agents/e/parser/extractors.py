"""
Code and metadata extraction utilities.

Provides functions to extract code blocks and metadata from various
markdown and response formats.
"""

from __future__ import annotations

import ast
import json
import re
from typing import Any, Optional


def extract_json_metadata(response: str) -> Optional[dict[str, Any]]:
    """
    Extract JSON metadata from response.

    Looks for ```json blocks anywhere in the response.
    Returns None if no valid JSON found.
    """
    json_match = re.search(
        r'```(?:json)?\s*\n(\{.*?\})\s*```',
        response,
        re.DOTALL | re.IGNORECASE
    )

    if not json_match:
        return None

    try:
        return json.loads(json_match.group(1).strip())
    except json.JSONDecodeError:
        return None


def extract_code_block(response: str, allow_unclosed: bool = True) -> Optional[str]:
    """
    Extract Python code block from response.

    Args:
        response: The LLM response text
        allow_unclosed: If True, try to extract from unclosed blocks

    Returns:
        Extracted code string, or None if no valid code found
    """
    # Try properly closed blocks first
    patterns = [
        r'```python\s*\n(.*?)```',
        r'```py\s*\n(.*?)```',
        r'```\s*\n(.*?)```',
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            try:
                ast.parse(candidate)
                return candidate
            except SyntaxError:
                continue

    # If no valid closed block and unclosed allowed, try unclosed blocks
    if allow_unclosed:
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
                candidate = _clean_unclosed_block(candidate)

                try:
                    ast.parse(candidate)
                    return candidate
                except SyntaxError:
                    continue

    return None


def _clean_unclosed_block(code: str) -> str:
    """
    Clean up unclosed code block by removing trailing non-code text.

    Looks for markdown-like syntax that indicates end of code.
    """
    lines = code.split('\n')
    code_lines = []

    for line in lines:
        # Stop if we hit markdown-like syntax (heading without space after #)
        if line.strip().startswith('#') and not line.strip().startswith('# '):
            break
        code_lines.append(line)

    return '\n'.join(code_lines).strip()


def extract_structured_blocks(response: str) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    """
    Extract code and metadata from structured markdown response.

    Expected format:
        ## METADATA
        ```json
        {"description": "...", ...}
        ```

        ## CODE
        ```python
        # code here
        ```

    Returns:
        (code, metadata) tuple, either may be None
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

    code = code_match.group(1).strip() if code_match else None
    metadata = None

    if metadata_match:
        try:
            metadata = json.loads(metadata_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return code, metadata


def infer_metadata_from_ast(code: str) -> dict[str, Any]:
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
