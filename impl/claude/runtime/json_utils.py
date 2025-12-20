"""
JSON utility functions for robust LLM response parsing.

Extracted from runtime/base.py as part of H5 (IMPROVEMENT_PLAN.md).
These utilities handle common LLM output issues:
- Markdown code blocks
- Truncated JSON
- Trailing commas
- Extra text before/after JSON
- Unterminated strings
"""

import json
import re
from typing import Any


def robust_json_parse(response: str, allow_partial: bool = True) -> dict[str, Any]:
    """
    Robust JSON parser that handles common LLM output issues.

    Handles:
    - Markdown code blocks (```json ... ```)
    - Truncated JSON (closes brackets)
    - Trailing commas
    - Extra text before/after JSON
    - Unterminated strings

    Args:
        response: Raw LLM response text
        allow_partial: If True, try to repair truncated JSON

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If JSON cannot be parsed even after repair attempts
    """
    text = response.strip()

    # Step 1: Extract JSON from markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
        else:
            # Unterminated code block - take everything after ```json
            text = text[start:].strip()
    elif "```" in text:
        # Generic code block
        start = text.find("```") + 3
        # Skip language identifier if on same line
        newline = text.find("\n", start)
        if newline > 0:
            start = newline + 1
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
        else:
            text = text[start:].strip()

    # Step 2: Find JSON boundaries if there's extra text
    first_brace = text.find("{")
    first_bracket = text.find("[")
    if first_brace < 0 and first_bracket < 0:
        raise ValueError("No JSON object or array found in response")

    if first_brace >= 0 and (first_bracket < 0 or first_brace < first_bracket):
        text = text[first_brace:]
        closer = "}"
        opener = "{"
    else:
        text = text[first_bracket:]
        closer = "]"
        opener = "["

    # Step 3: Try direct parse first
    try:
        result: dict[str, Any] = json.loads(text)
        return result
    except json.JSONDecodeError:
        pass

    # Step 4: Try to repair common issues
    if allow_partial:
        repaired = _repair_json(text, opener, closer)
        try:
            result = json.loads(repaired)
            return result
        except json.JSONDecodeError:
            pass

    # Step 5: Last resort - try to extract any valid JSON object
    # Look for outermost balanced braces/brackets
    depth = 0
    start_pos = -1
    for i, char in enumerate(text):
        if char == opener:
            if depth == 0:
                start_pos = i
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0 and start_pos >= 0:
                candidate = text[start_pos : i + 1]
                try:
                    result = json.loads(candidate)
                    return result
                except json.JSONDecodeError:
                    pass

    raise ValueError(f"Could not parse JSON from response: {text[:200]}...")


def _repair_json(text: str, opener: str, closer: str) -> str:
    """
    Attempt to repair truncated or malformed JSON.

    Strategies:
    - Remove trailing commas
    - Close unterminated strings
    - Balance brackets/braces
    - Handle embedded code with unescaped characters
    """
    # Remove trailing commas before closers
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Try to find and fix unterminated strings containing code
    # This is tricky - we need to find the last properly escaped string
    repaired = text

    # Count unescaped quotes (not preceded by backslash)
    # This is a simplified heuristic
    in_string = False
    escaped = False
    quote_positions = []

    for i, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            quote_positions.append(i)
            in_string = not in_string

    # If odd number of quotes, string is unterminated
    if len(quote_positions) % 2 == 1:
        # Add closing quote
        repaired = repaired.rstrip()
        if not repaired.endswith('"'):
            repaired += '"'

    # Count brackets to see if we need to close
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")

    # Close brackets and braces
    repaired += "]" * open_brackets
    repaired += "}" * open_braces

    return repaired


def _extract_field_values(text: str, fields: list[str]) -> dict[str, Any]:
    """
    Extract specific field values from malformed JSON using regex.

    Fallback for when JSON repair fails but we need specific fields.
    """
    result = {}

    for field in fields:
        # Match "field": "value" or "field": value patterns
        pattern = rf'"{field}"\s*:\s*("([^"\\]|\\.)*"|[^,\}}\]]+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            # Try to parse the value
            if value.startswith('"') and value.endswith('"'):
                result[field] = value[1:-1]  # Remove quotes
            elif value.lower() in ("true", "false"):
                result[field] = value.lower() == "true"
            elif value.lower() == "null":
                result[field] = None
            else:
                try:
                    result[field] = float(value) if "." in value else int(value)
                except ValueError:
                    result[field] = value

    return result


def json_response_parser(response: str) -> dict[str, Any]:
    """Standard JSON response parser with markdown code block handling."""
    return robust_json_parse(response, allow_partial=True)


def parse_structured_sections(response: str, section_names: list[str]) -> dict[str, list[str]]:
    """
    Parse structured sections from LLM response.

    Looks for section headers (e.g., "RESPONSES:", "FOLLOW-UPS:") and extracts
    content as lists. Handles both numbered lists (1. item) and bullet lists (- item).

    Args:
        response: The LLM response text
        section_names: List of section names to look for (case-insensitive)

    Returns:
        Dict mapping section names to lists of extracted items

    Example:
        >>> response = '''
        ... RESPONSES:
        ... 1. First response
        ... 2. Second response
        ...
        ... FOLLOW-UPS:
        ... - First question?
        ... - Second question?
        ... '''
        >>> parse_structured_sections(response, ["responses", "follow-ups"])
        {'responses': ['First response', 'Second response'],
         'follow-ups': ['First question?', 'Second question?']}
    """
    result: dict[str, list[str]] = {}
    lines = response.split("\n")

    # Build regex patterns for section headers (case-insensitive)
    # Match "SECTION_NAME:" or "SECTION-NAME:" or "SECTION NAME:"
    section_patterns = {}
    for name in section_names:
        # Normalize name for pattern matching (replace underscores/hyphens with flexible pattern)
        pattern_name = name.replace("_", r"[\s_-]").replace("-", r"[\s_-]")
        pattern = re.compile(rf"^{pattern_name}\s*:\s*$", re.IGNORECASE)
        section_patterns[name] = pattern

    current_section: str | None = None
    current_items: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Check if this line is a section header
        found_section = False
        for section_name, pattern in section_patterns.items():
            if pattern.match(stripped):
                # Save previous section if any
                if current_section and current_items:
                    result[current_section] = current_items

                # Start new section
                current_section = section_name
                current_items = []
                found_section = True
                break

        if found_section:
            continue

        # If we're in a section, try to extract list items
        if current_section:
            # Match numbered lists: "1. item" or "1) item"
            numbered_match = re.match(r"^\d+[\.\)]\s+(.+)$", stripped)
            if numbered_match:
                current_items.append(numbered_match.group(1))
                continue

            # Match bullet lists: "- item" or "* item"
            bullet_match = re.match(r"^[-\*]\s+(.+)$", stripped)
            if bullet_match:
                current_items.append(bullet_match.group(1))
                continue

    # Save last section
    if current_section and current_items:
        result[current_section] = current_items

    return result
