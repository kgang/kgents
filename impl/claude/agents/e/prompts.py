"""
Prompt Engineering: Rich context builders for high-quality code generation.

This module implements Layer 1 of the Evolution Reliability Plan:
- Type-aware prompting with explicit signature requirements
- Complete constructor examples and scaffolding
- Pre-existing error awareness
- Structural validation rules

Goals:
- Reduce syntax errors from ~20-30% to <10%
- Provide clear, unambiguous requirements to LLMs
- Include context from similar successful patterns
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .ast_analyzer import CodeStructure
from .experiment import CodeModule


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
    type_annotations: dict[str, str]  # name → type signature
    imports: list[str]
    pre_existing_errors: list[str]  # from mypy
    similar_patterns: list[str]  # from codebase grep
    principles: list[str]  # kgents principles to follow
    complexity_hints: list[str] = field(default_factory=list)

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
        similar_patterns = find_similar_patterns(ast_structure, module.path.parent.parent)

    # Get relevant principles
    principles = get_relevant_principles(module.category)

    # Complexity hints from AST
    complexity_hints = []
    if ast_structure:
        complexity_hints = list(ast_structure.complexity_hints)

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
    )


def extract_type_annotations(code: str) -> dict[str, str]:
    """
    Extract type annotations from Python code.

    Returns a mapping of symbol names to their type signatures.
    Example: {"invoke": "async def invoke(self, input: A) -> B"}
    """
    annotations: dict[str, str] = {}

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return annotations

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                sig = ast.unparse(node).split(":", 1)[0]
                if node.returns:
                    sig += f" -> {ast.unparse(node.returns)}"
                annotations[node.name] = sig
            except Exception:
                pass

        elif isinstance(node, ast.ClassDef):
            try:
                bases_str = ""
                if node.bases:
                    bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})"
                annotations[node.name] = f"class {node.name}{bases_str}"
            except Exception:
                pass

    return annotations


def extract_imports(code: str) -> list[str]:
    """Extract import statements from code."""
    imports = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_line = f"import {alias.name}"
                if alias.asname:
                    import_line += f" as {alias.asname}"
                imports.append(import_line)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = "." * node.level
            for alias in node.names:
                import_line = f"from {level}{module} import {alias.name}"
                if alias.asname:
                    import_line += f" as {alias.asname}"
                imports.append(import_line)

    return imports


def check_existing_errors(path: Path) -> list[str]:
    """
    Check for pre-existing type/syntax errors in a module.

    Runs mypy in strict mode and captures errors.
    Returns list of error messages.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(path), "--strict", "--no-error-summary"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Parse errors from mypy output
            errors = []
            for line in result.stdout.split("\n"):
                if line.strip() and path.name in line:
                    # Extract just the error message
                    if "error:" in line:
                        error_msg = line.split("error:", 1)[1].strip()
                        errors.append(error_msg)

            return errors[:10]  # Limit to first 10 errors

        return []

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def find_similar_patterns(structure: CodeStructure, base_path: Path) -> list[str]:
    """
    Find similar code patterns from successful modules.

    Searches the codebase for examples of similar classes/functions
    that can serve as scaffolding examples.
    """
    patterns = []

    # Look for similar class patterns
    for cls in structure.classes[:2]:  # Just first 2 classes
        cls_name = cls["name"]
        bases = cls.get("bases", [])

        if bases:
            # Search for other classes with same base
            try:
                import subprocess
                result = subprocess.run(
                    ["grep", "-r", "-n", "--include=*.py", f"class.*({bases[0]})", str(base_path)],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if result.returncode == 0:
                    # Get first few matches
                    matches = result.stdout.split("\n")[:3]
                    for match in matches:
                        if match.strip() and structure.module_name not in match:
                            patterns.append(f"Similar class pattern: {match.split(':', 2)[-1].strip()}")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    return patterns


def get_relevant_principles(module_category: str) -> list[str]:
    """
    Get relevant kgents principles for a module category.

    Different categories emphasize different principles:
    - bootstrap: Composability, minimalism
    - agents: Domain-specific guidance
    - runtime: Performance, reliability
    """
    core_principles = [
        "Composable: Agents are morphisms; composition is primary",
        "Tasteful: Quality over quantity",
        "Type-safe: Use strict type annotations (A → B morphisms)",
    ]

    category_principles = {
        "bootstrap": [
            "Minimal: Bootstrap agents should be simple and foundational",
            "Generic: Work with any type parameters A, B",
        ],
        "agents": [
            "Domain-specific: Embody a clear domain concept",
            "Curated: Intentional, not comprehensive",
        ],
        "runtime": [
            "Reliable: Handle errors gracefully",
            "Efficient: Minimize LLM calls",
        ],
    }

    return core_principles + category_principles.get(module_category, [])


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
        return "✓ No pre-existing errors"

    lines = [f"⚠️ {len(errors)} pre-existing error(s):"]
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


def build_improvement_prompt(
    hypothesis: str,
    context: PromptContext,
    improvement_type: str = "refactor"
) -> str:
    """
    Build a comprehensive prompt for code improvement.

    This prompt includes:
    1. Clear type signature requirements
    2. Complete constructor examples
    3. Pre-existing error warnings
    4. Structural validation rules
    5. Similar patterns as scaffolding
    6. Relevant principles to follow

    Args:
        hypothesis: The improvement hypothesis
        context: Rich prompt context
        improvement_type: Type of improvement (refactor, fix, feature, test)

    Returns:
        Complete prompt string ready for LLM
    """
    return f"""# Code Improvement Task

## Hypothesis
{hypothesis}

## Current Code Structure
File: {context.module_path}
Module: {context.module_name}
Classes: {', '.join(context.class_names) if context.class_names else '(none)'}
Functions: {', '.join(context.function_names) if context.function_names else '(none)'}
Lines: {len(context.current_code.splitlines())}

## Type Signatures (MUST PRESERVE OR IMPROVE)
{format_type_signatures(context.type_annotations)}

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


def build_simple_prompt(hypothesis: str, module: CodeModule) -> str:
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
