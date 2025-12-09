"""
G-gent Phase 3: AST Renderer

This module provides AST-to-text rendering for round-trip validation.

Rendering is the inverse of parsing:
- parse(text) → AST
- render(AST) → text
- parse(render(AST)) ≈ AST (round-trip property)
"""

from typing import Any
from agents.g.types import GrammarFormat, GrammarLevel


def render_ast(ast: Any, format: GrammarFormat, level: GrammarLevel) -> str:
    """
    Render AST back to text representation.

    Args:
        ast: Abstract syntax tree (dict, list, or primitive)
        format: Grammar format (determines rendering strategy)
        level: Grammar level (SCHEMA, COMMAND, RECURSIVE)

    Returns:
        Text representation that can be re-parsed
    """
    if format == GrammarFormat.PYDANTIC:
        return _render_pydantic(ast)
    elif format in (GrammarFormat.BNF, GrammarFormat.EBNF):
        return _render_command(ast)
    elif format == GrammarFormat.LARK:
        return _render_recursive(ast)
    else:
        # Fallback: JSON-like representation
        return _render_default(ast)


# ============================================================================
# Format-Specific Renderers
# ============================================================================


def _render_pydantic(ast: Any) -> str:
    """
    Render Pydantic schema AST (Level 1).

    AST format: dict with field → value mappings
    Output: Python dict literal or constructor call
    """
    if not isinstance(ast, dict):
        return str(ast)

    # Render as Python dict literal
    items = []
    for key, value in ast.items():
        if isinstance(value, str):
            items.append(f'"{key}": "{value}"')
        elif isinstance(value, (int, float, bool)):
            items.append(f'"{key}": {value}')
        elif isinstance(value, list):
            list_repr = (
                "["
                + ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in value)
                + "]"
            )
            items.append(f'"{key}": {list_repr}')
        else:
            items.append(f'"{key}": {value}')

    return "{" + ", ".join(items) + "}"


def _render_command(ast: Any) -> str:
    """
    Render BNF command AST (Level 2).

    AST format: {"verb": str, "noun": str | None}
    Output: "VERB NOUN" or just "VERB"
    """
    if not isinstance(ast, dict):
        return str(ast)

    verb = ast.get("verb", "")
    noun = ast.get("noun")

    if noun:
        return f"{verb} {noun}"
    else:
        return verb


def _render_recursive(ast: Any) -> str:
    """
    Render Lark recursive AST (Level 3).

    AST format: {"type": str, "children": list}
    Output: S-expression or nested structure
    """
    if not isinstance(ast, dict):
        return str(ast)

    node_type = ast.get("type", "node")
    children = ast.get("children", [])

    if not children:
        return f"({node_type})"

    # Render children recursively
    rendered_children = [_render_recursive(child) for child in children]

    # S-expression format
    return f"({node_type} {' '.join(rendered_children)})"


def _render_default(ast: Any) -> str:
    """
    Default fallback renderer.

    Renders as JSON-like structure.
    """
    if isinstance(ast, dict):
        items = [f"{k}: {_render_default(v)}" for k, v in ast.items()]
        return "{" + ", ".join(items) + "}"
    elif isinstance(ast, list):
        items = [_render_default(item) for item in ast]
        return "[" + ", ".join(items) + "]"
    elif isinstance(ast, str):
        return f'"{ast}"'
    else:
        return str(ast)


# ============================================================================
# Round-Trip Validation
# ============================================================================


def validate_round_trip(tongue: Any, text: str) -> tuple[bool, str]:
    """
    Validate round-trip: parse → render → parse.

    Args:
        tongue: Tongue artifact with parse() and render() methods
        text: Original input text

    Returns:
        (success, message) tuple
    """
    try:
        # Parse original text
        parse1 = tongue.parse(text)

        if not parse1.success:
            return (False, f"Initial parse failed: {parse1.error}")

        ast1 = parse1.ast

        # Render AST back to text
        rendered = tongue.render(ast1)

        # Parse rendered text
        parse2 = tongue.parse(rendered)

        if not parse2.success:
            return (False, f"Re-parse failed: {parse2.error}")

        ast2 = parse2.ast

        # Compare ASTs (approximately equal)
        if ast1 == ast2:
            return (
                True,
                "Round-trip successful: parse(render(parse(text))) == parse(text)",
            )
        else:
            return (
                False,
                f"ASTs differ:\n  Original: {ast1}\n  After round-trip: {ast2}",
            )

    except Exception as e:
        return (False, f"Round-trip validation error: {e}")
