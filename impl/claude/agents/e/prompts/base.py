"""
Base prompt context structures and builders.

This module contains:
- PromptContext: Rich context dataclass for code generation
- build_prompt_context: Main builder function
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..ast_analyzer import CodeStructure
from ..experiment import CodeModule
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


@dataclass
class PromptContext:
    """
    Rich context for code generation prompts.

    Contains all information needed to generate high-quality,
    type-safe, syntactically valid code improvements.
    """

    module_path: Path
    current_code: str
    ast_structure: Optional[CodeStructure]
    type_annotations: dict[str, str]  # name -> type signature
    imports: list[str]
    pre_existing_errors: list[str]  # from mypy
    similar_patterns: list[str]  # from codebase grep
    principles: list[str]  # kgents principles to follow
    complexity_hints: list[str] = field(default_factory=list)
    # API stubs to prevent hallucinations
    dataclass_fields: dict[str, list[tuple[str, str]]] = field(
        default_factory=dict
    )  # class -> [(field, type)]
    enum_values: dict[str, list[str]] = field(default_factory=dict)  # enum -> [values]
    imported_apis: dict[str, str] = field(default_factory=dict)  # API -> signature

    @property
    def module_name(self) -> str:
        """Get the module name from path."""
        return self.module_path.stem

    @property
    def class_names(self) -> list[str]:
        """Extract class names from AST structure."""
        if not self.ast_structure:
            return []
        return [cls["name"] for cls in self.ast_structure.classes]

    @property
    def function_names(self) -> list[str]:
        """Extract function names from AST structure."""
        if not self.ast_structure:
            return []
        return [func["name"] for func in self.ast_structure.functions]


def build_prompt_context(
    module: CodeModule,
    ast_structure: Optional[CodeStructure] = None,
) -> PromptContext:
    """
    Build rich prompt context for a module.

    Gathers all information needed for high-quality code generation:
    - Current code and AST structure
    - Type annotations from source
    - Pre-existing errors from mypy
    - Similar patterns from successful modules
    - Relevant kgents principles
    """
    current_code = module.path.read_text()

    # Extract type annotations
    type_annotations = extract_type_annotations(current_code)

    # Extract imports
    imports = extract_imports(current_code)

    # Check for pre-existing errors
    pre_existing_errors = check_existing_errors(module.path)

    # Find similar patterns (if AST structure available)
    similar_patterns = []
    if ast_structure and ast_structure.classes:
        similar_patterns = find_similar_patterns(
            ast_structure, module.path.parent.parent
        )

    # Get relevant principles
    principles = get_relevant_principles(module.category)

    # Complexity hints from AST
    complexity_hints = []
    if ast_structure:
        complexity_hints = list(ast_structure.complexity_hints)

    # Extract API stubs to prevent hallucinations
    dataclass_fields = extract_dataclass_fields(current_code)
    enum_values = extract_enum_values(current_code)
    imported_apis = extract_api_signatures(imports, module.path.parent)

    return PromptContext(
        module_path=module.path,
        current_code=current_code,
        ast_structure=ast_structure,
        type_annotations=type_annotations,
        imports=imports,
        pre_existing_errors=pre_existing_errors,
        similar_patterns=similar_patterns,
        principles=principles,
        complexity_hints=complexity_hints,
        dataclass_fields=dataclass_fields,
        enum_values=enum_values,
        imported_apis=imported_apis,
    )
