"""
Code repair utilities for handling truncated or incomplete LLM output.

Provides functions to repair common issues:
- Unclosed triple-quoted strings (especially f-strings)
- Incomplete function bodies
- Truncated statements
"""

from __future__ import annotations


def repair_truncated_strings(code: str) -> tuple[str, list[str]]:
    """
    Attempt to repair truncated triple-quoted strings.

    Common issue: LLM runs out of tokens mid-f-string.
    Returns (repaired_code, list_of_repairs_made).
    """
    repairs: list[str] = []

    # Count open triple quotes
    triple_double = code.count('"""')
    triple_single = code.count("'''")

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

    return repaired, repairs


def repair_incomplete_function(code: str) -> tuple[str, list[str]]:
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


def apply_repairs(code: str) -> tuple[str, list[str]]:
    """
    Apply all available repair strategies to code.

    Returns (repaired_code, list_of_repairs_applied).
    """
    all_repairs: list[str] = []

    # String repairs
    repaired, string_repairs = repair_truncated_strings(code)
    all_repairs.extend(string_repairs)

    # Function repairs
    repaired, func_repairs = repair_incomplete_function(repaired)
    all_repairs.extend(func_repairs)

    return repaired, all_repairs
