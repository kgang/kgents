"""
Prompt formatting and improvement prompt generation.

This module contains:
- Formatting functions for prompt sections
- build_improvement_prompt: Full prompt with rich context
- build_simple_prompt: Fallback prompt without full context
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import PromptContext
    from ..experiment import CodeModule


def format_type_signatures(annotations: dict[str, str]) -> str:
    """Format type signature dictionary for display in prompt."""
    if not annotations:
        return "(No type annotations found)"

    lines = []
    for name, sig in list(annotations.items())[:10]:  # Limit to 10
        lines.append(f"  - {name}: {sig}")

    if len(annotations) > 10:
        lines.append(f"  ... and {len(annotations) - 10} more")

    return "\n".join(lines)


def format_errors(errors: list[str]) -> str:
    """Format error list for display in prompt."""
    if not errors:
        return "No pre-existing errors"

    lines = [f"{len(errors)} pre-existing error(s):"]
    for i, error in enumerate(errors[:5], 1):
        lines.append(f"  {i}. {error}")

    if len(errors) > 5:
        lines.append(f"  ... and {len(errors) - 5} more")

    return "\n".join(lines)


def format_patterns(patterns: list[str]) -> str:
    """Format similar patterns for display in prompt."""
    if not patterns:
        return "(No similar patterns found)"

    return "\n".join(f"  - {p}" for p in patterns[:3])


def format_principles(principles: list[str]) -> str:
    """Format principles for display in prompt."""
    return "\n".join(f"  - {p}" for p in principles)


def format_dataclass_fields(fields_map: dict[str, list[tuple[str, str]]]) -> str:
    """Format dataclass field definitions for display in prompt."""
    if not fields_map:
        return "(No dataclasses found)"

    lines = []
    for class_name, fields in list(fields_map.items())[:5]:  # Limit to 5 classes
        fields_str = ", ".join(
            f"{name}: {typ}" for name, typ in fields[:8]
        )  # First 8 fields
        if len(fields) > 8:
            fields_str += f" ... (+{len(fields) - 8} more)"
        lines.append(f"  @dataclass {class_name}({fields_str})")

    if len(fields_map) > 5:
        lines.append(f"  ... and {len(fields_map) - 5} more dataclasses")

    return "\n".join(lines)


def format_enum_values(enum_map: dict[str, list[str]]) -> str:
    """Format enum values for display in prompt."""
    if not enum_map:
        return "(No enums found)"

    lines = []
    for enum_name, values in list(enum_map.items())[:5]:  # Limit to 5 enums
        values_str = ", ".join(values)
        lines.append(f"  {enum_name}: {values_str}")

    if len(enum_map) > 5:
        lines.append(f"  ... and {len(enum_map) - 5} more enums")

    return "\n".join(lines)


def format_imported_apis(api_map: dict[str, str]) -> str:
    """Format imported API signatures for display in prompt."""
    if not api_map:
        return "(No imported APIs extracted)"

    lines = []
    for api_name, sig in list(api_map.items())[:10]:  # Limit to 10 APIs
        lines.append(f"  {api_name}: {sig}")

    if len(api_map) > 10:
        lines.append(f"  ... and {len(api_map) - 10} more APIs")

    return "\n".join(lines)


def build_improvement_prompt(
    hypothesis: str, context: "PromptContext", improvement_type: str = "refactor"
) -> str:
    """
    Build a comprehensive prompt for code improvement.

    This prompt includes:
    1. Clear type signature requirements
    2. Complete constructor examples
    3. Core API reference (prevents hallucination)
    4. Pre-existing error warnings
    5. Structural validation rules
    6. Similar patterns as scaffolding
    7. Relevant principles to follow

    Args:
        hypothesis: The improvement hypothesis
        context: Rich prompt context
        improvement_type: Type of improvement (refactor, fix, feature, test)

    Returns:
        Complete prompt string ready for LLM
    """
    # Import API signatures module
    from ..api_signatures import get_kgents_api_reference

    api_reference = get_kgents_api_reference()

    return f"""# Code Improvement Task

## Hypothesis
{hypothesis}

## Current Code Structure
File: {context.module_path}
Module: {context.module_name}
Classes: {", ".join(context.class_names) if context.class_names else "(none)"}
Functions: {", ".join(context.function_names) if context.function_names else "(none)"}
Lines: {len(context.current_code.splitlines())}

## Type Signatures (MUST PRESERVE OR IMPROVE)
{format_type_signatures(context.type_annotations)}

{api_reference}

## Module-Specific APIs (FROM CURRENT FILE)

### Dataclass Constructors
{format_dataclass_fields(context.dataclass_fields)}

### Enum Values
{format_enum_values(context.enum_values)}

### Imported Module APIs
{format_imported_apis(context.imported_apis)}

## Pre-Existing Issues (DO NOT INTRODUCE MORE)
{format_errors(context.pre_existing_errors)}

## Patterns from Similar Code
{format_patterns(context.similar_patterns)}

## CRITICAL REQUIREMENTS

### 1. Complete Type Signatures
- All function parameters MUST have type annotations
- All function return types MUST be annotated
- Generic types MUST have correct parameter counts (e.g., Agent[A, B], not Agent[A,])
- Example: `async def invoke(self, input: A) -> B:`

### 2. Valid Constructors
- All dataclass fields MUST have types and defaults if optional
- All classes MUST be instantiable (have __init__ or @dataclass)
- Example: `@dataclass\\nclass Foo:\\n    field: str = "default"`

### 3. Complete File Contents
- Return ENTIRE file contents, not fragments
- Include ALL imports from original file
- Include ALL classes and functions (even if unchanged)
- Do not use `# ... rest of file unchanged ...` comments

### 4. Syntax Validation
- Code MUST be valid Python (parse with ast.parse())
- All brackets, parens, quotes MUST be closed
- No placeholder code (TODO, pass, ...)
- No incomplete generic types (Maybe[, Fix[A,B] when Fix[A] expected)

### 5. Mypy Compliance
- Code should pass `mypy --strict` or at minimum not introduce NEW errors
- If pre-existing errors exist, you may match that count but not exceed it
- Pay special attention to generic type parameters

### 6. Principles to Follow
{format_principles(context.principles)}

## Output Format

Your response MUST follow this EXACT format:

### METADATA (JSON)
```json
{{
  "description": "Brief description of the improvement (1-2 sentences)",
  "rationale": "Why this improves the code",
  "improvement_type": "{improvement_type}",
  "confidence": 0.8,
  "changed_symbols": ["symbol1", "symbol2"],
  "risk_level": "low"
}}
```

### CODE (Complete Python file)
```python
# Complete file contents here
# MUST include all imports at the top
# MUST include all classes/functions (even unchanged ones)
# MUST have valid type signatures on all functions
# MUST be syntactically valid Python

{context.current_code[:500]}
# ... (your improved version of the complete file)
```

## Validation Checklist

Before returning your response, verify:
- [ ] All type annotations are complete and correct
- [ ] All generic types have correct parameter counts
- [ ] All imports are present
- [ ] Code is complete (no fragments or TODOs)
- [ ] Syntax is valid (would parse with ast.parse())
- [ ] You're not introducing more errors than already exist
- [ ] The improvement aligns with kgents principles

Generate the improvement following these requirements EXACTLY.
"""


def build_simple_prompt(hypothesis: str, module: "CodeModule") -> str:
    """
    Build a simple prompt without full context (fallback for errors).

    Use this when full context building fails or for quick experiments.
    """
    code = module.path.read_text()

    return f"""# Code Improvement Task

## Hypothesis
{hypothesis}

## Current Code
File: {module.path}

```python
{code}
```

## Requirements

1. Return complete, valid Python code
2. Include all imports
3. Maintain or improve type annotations
4. Follow the hypothesis exactly
5. Ensure code passes syntax and type checks

## Output Format

```python
# Your complete improved file here
```
"""
