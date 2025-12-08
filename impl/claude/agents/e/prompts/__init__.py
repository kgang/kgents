"""
Prompt Engineering: Rich context builders for high-quality code generation.

Split into:
- base: Core data structures (PromptContext) and context building
- analysis: Code analysis utilities (extract types, imports, dataclasses, enums)
- improvement: Prompt formatting and improvement prompt generation
"""

from .base import PromptContext, build_prompt_context
from .analysis import (
    extract_type_annotations,
    extract_imports,
    extract_dataclass_fields,
    extract_enum_values,
    extract_api_signatures,
    check_existing_errors,
    find_similar_patterns,
    get_relevant_principles,
)
from .improvement import (
    format_type_signatures,
    format_errors,
    format_patterns,
    format_principles,
    format_dataclass_fields,
    format_enum_values,
    format_imported_apis,
    build_improvement_prompt,
    build_simple_prompt,
)

__all__ = [
    # base
    "PromptContext",
    "build_prompt_context",
    # analysis
    "extract_type_annotations",
    "extract_imports",
    "extract_dataclass_fields",
    "extract_enum_values",
    "extract_api_signatures",
    "check_existing_errors",
    "find_similar_patterns",
    "get_relevant_principles",
    # improvement
    "format_type_signatures",
    "format_errors",
    "format_patterns",
    "format_principles",
    "format_dataclass_fields",
    "format_enum_values",
    "format_imported_apis",
    "build_improvement_prompt",
    "build_simple_prompt",
]
