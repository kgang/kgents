"""
Fallback Strategy: Progressive simplification for failed experiments.

This module implements Layer 3b of the Evolution Reliability Plan:
- When primary improvement fails, try progressively simpler approaches
- Strategy waterfall: full → minimal → type-only → docs → skip
- Ensures we capture some value even from complex/risky changes

Goals:
- Increase incorporation rate by accepting partial improvements
- Avoid all-or-nothing failures
- Provide graceful degradation path
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Optional

from .ast_analyzer import CodeStructure
from .experiment import Experiment, ExperimentStatus, CodeModule
from .prompts import PromptContext, build_simple_prompt


@dataclass
class FallbackConfig:
    """Configuration for fallback strategy."""
    enable_minimal: bool = True
    enable_type_only: bool = True
    enable_docs_only: bool = True
    verbose: bool = False


@dataclass
class FallbackLevel:
    """A level in the fallback hierarchy."""
    name: str
    description: str
    complexity: int  # 1-5, lower is simpler


@dataclass
class FallbackResult:
    """Result of fallback strategy execution."""
    success: bool
    level_reached: Optional[FallbackLevel] = None
    experiment: Optional[Experiment] = None
    attempts: list[str] = None  # type: ignore
    reason_for_fallback: str = ""

    def __post_init__(self) -> None:
        if self.attempts is None:
            self.attempts = []


class FallbackStrategy:
    """
    When primary improvement fails, try progressively simpler approaches.

    Strategy waterfall (from complex to simple):
    1. Original hypothesis (full improvement) - already tried
    2. Minimal version (single function/class)
    3. Type-only fix (just add/fix type annotations)
    4. Documentation-only (add docstrings/comments)
    5. Skip (record as too complex for now)

    Each level is simpler and safer than the last, maximizing
    the chance of incorporating *some* improvement.

    Morphism (conceptually): FailedExperiment × Context → SimplerExperiment | None
    """

    # Define fallback levels
    LEVEL_MINIMAL = FallbackLevel("minimal", "Improve single function/class", 3)
    LEVEL_TYPE_ONLY = FallbackLevel("type_only", "Add/fix type annotations only", 2)
    LEVEL_DOCS_ONLY = FallbackLevel("docs_only", "Add documentation only", 1)

    def __init__(self, config: Optional[FallbackConfig] = None):
        """Initialize fallback strategy with configuration."""
        self.config = config or FallbackConfig()

    def should_fallback(
        self,
        experiment: Experiment,
        retry_exhausted: bool = False
    ) -> bool:
        """
        Determine if we should try fallback strategies.

        Fallback is appropriate when:
        - Original experiment failed
        - Retries have been exhausted
        - Failure wasn't due to fundamental module issues
        """
        if experiment.status == ExperimentStatus.PASSED:
            return False

        if not retry_exhausted:
            return False  # Try retry first

        # Don't fallback if the module itself has issues
        if experiment.error and "module" in experiment.error.lower():
            return False

        return True

    def generate_minimal_prompt(
        self,
        original_hypothesis: str,
        context: PromptContext,
        target_symbol: Optional[str] = None
    ) -> str:
        """
        Generate prompt for minimal version: improve just one function/class.

        If target_symbol is provided, focus on that. Otherwise, identify
        the most relevant symbol from the hypothesis.
        """
        if not target_symbol:
            target_symbol = self._identify_primary_target(
                original_hypothesis,
                context.ast_structure
            )

        if not target_symbol:
            # Fallback to first function/class
            if context.function_names:
                target_symbol = context.function_names[0]
            elif context.class_names:
                target_symbol = context.class_names[0]
            else:
                target_symbol = "the main component"

        return f"""
# Minimal Improvement Task (Fallback Strategy)

**Original hypothesis was too complex. Let's try a minimal version.**

## Original Hypothesis
{original_hypothesis}

## Minimal Scope
Improve ONLY the `{target_symbol}` function/class.

**CONSTRAINTS (CRITICAL):**
1. Change ONLY `{target_symbol}` - nothing else
2. Preserve all other code exactly as-is
3. Make a small, safe, focused improvement
4. Ensure the change is minimal and low-risk
5. Return the COMPLETE file with only `{target_symbol}` modified

**This is a fallback after a larger change failed.**
**Focus on making the smallest possible improvement that adds value.**

## Context
Module: {context.module_path.name}
Current imports: {len(context.imports)} imports
Functions: {', '.join(context.function_names[:5])}
Classes: {', '.join(context.class_names[:5])}

## Output Format
Return the complete Python file with your minimal change to `{target_symbol}`.
All other code should remain unchanged.
"""

    def generate_type_only_prompt(
        self,
        original_hypothesis: str,
        context: PromptContext
    ) -> str:
        """
        Generate prompt for type-only fix: just add/fix type annotations.

        This is a very safe fallback - type annotations don't change behavior,
        only improve type safety and documentation.
        """
        # Identify functions/methods missing type annotations
        missing_annotations = self._find_missing_type_annotations(context.current_code)

        targets = ", ".join(missing_annotations[:5]) if missing_annotations else "all functions"

        return f"""
# Type Annotation Task (Safe Fallback)

**Original hypothesis was too complex. Let's just improve type safety.**

## Original Hypothesis
{original_hypothesis}

## Simplified Task
Add or fix type annotations ONLY. Do not change any logic.

**TARGETS:**
{targets}

**CONSTRAINTS (CRITICAL):**
1. Add type annotations to function parameters and return types
2. Fix any incomplete generic types (Maybe[, Agent[A,], etc.)
3. DO NOT change any logic or behavior
4. DO NOT add new functionality
5. DO NOT refactor code structure
6. Return COMPLETE file with only type annotations added/fixed

**This is the safest possible improvement - types only.**

## Context
Module: {context.module_path.name}
Current type annotations: {len(context.type_annotations)}
Missing annotations: {len(missing_annotations)} functions

## Requirements
- Use proper typing imports: `from typing import Optional, Any, ...`
- Follow existing type annotation style in the codebase
- Preserve all existing type hints exactly
- All generic types must be complete: `Maybe[str]`, `Agent[A, B]`

## Output Format
Return the complete Python file with type annotations added/fixed.
No other changes allowed.
"""

    def generate_docs_only_prompt(
        self,
        original_hypothesis: str,
        context: PromptContext
    ) -> str:
        """
        Generate prompt for documentation-only: add docstrings/comments.

        This is the safest fallback - documentation has zero behavior impact
        but still adds value for maintainability.
        """
        # Identify functions/classes missing docstrings
        missing_docs = self._find_missing_docstrings(context.current_code)

        targets = ", ".join(missing_docs[:5]) if missing_docs else "main functions"

        return f"""
# Documentation Task (Safest Fallback)

**Original hypothesis was too complex. Let's just improve documentation.**

## Original Hypothesis
{original_hypothesis}

## Simplified Task
Add docstrings and comments ONLY. Do not change any code.

**TARGETS:**
{targets}

**CONSTRAINTS (CRITICAL):**
1. Add docstrings to functions and classes
2. Add inline comments for complex logic
3. DO NOT change any code whatsoever
4. DO NOT change indentation (except for adding docstrings)
5. Return COMPLETE file with only docstrings/comments added

**This is pure documentation - zero behavior change.**

## Context
Module: {context.module_path.name}
Functions: {len(context.function_names)}
Classes: {len(context.class_names)}
Missing docstrings: {len(missing_docs)}

## Documentation Style
Follow Google-style docstrings:
```python
def function(param1: str, param2: int) -> bool:
    '''
    Brief description.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    '''
```

## Output Format
Return the complete Python file with docstrings added.
No code changes allowed - documentation only.
"""

    def _identify_primary_target(
        self,
        hypothesis: str,
        ast_structure: Optional[CodeStructure]
    ) -> Optional[str]:
        """
        Identify the primary function/class mentioned in hypothesis.

        Uses text matching to find the most relevant symbol.
        """
        if not ast_structure:
            return None

        hypothesis_lower = hypothesis.lower()

        # Check for explicit mentions of functions
        for func in ast_structure.functions:
            func_name = str(func["name"])
            if func_name.lower() in hypothesis_lower:
                return func_name

        # Check for explicit mentions of classes
        for cls in ast_structure.classes:
            cls_name = str(cls["name"])
            if cls_name.lower() in hypothesis_lower:
                return cls_name

        # Fallback: return first function or class
        if ast_structure.functions:
            return str(ast_structure.functions[0]["name"])
        if ast_structure.classes:
            return str(ast_structure.classes[0]["name"])

        return None

    def _find_missing_type_annotations(self, code: str) -> list[str]:
        """
        Find functions missing type annotations.

        Returns list of function names that lack parameter or return type annotations.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        missing = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip dunder methods (often don't need annotations)
                if node.name.startswith("__") and node.name.endswith("__"):
                    continue

                # Check if return type is annotated
                has_return_annotation = node.returns is not None

                # Check if all params are annotated
                has_param_annotations = all(
                    arg.annotation is not None
                    for arg in node.args.args
                    if arg.arg != "self" and arg.arg != "cls"
                )

                if not (has_return_annotation and has_param_annotations):
                    missing.append(node.name)

        return missing

    def _find_missing_docstrings(self, code: str) -> list[str]:
        """
        Find functions and classes missing docstrings.

        Returns list of symbol names lacking docstrings.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        missing = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check if has docstring (first statement is string)
                has_docstring = (
                    len(node.body) > 0 and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))
                )

                if not has_docstring:
                    missing.append(node.name)

        return missing


# Singleton instance
fallback_strategy = FallbackStrategy()
