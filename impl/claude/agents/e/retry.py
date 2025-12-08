"""
Retry Strategy: Intelligent retry with failure-aware prompt refinement.

This module implements Layer 3a of the Evolution Reliability Plan:
- Retry failed experiments with refined prompts
- Learn from failure and adjust approach
- Categorize failures to apply targeted fixes
- Maximum retry attempts to avoid infinite loops

Goals:
- Increase incorporation rate from ~30-50% to >90%
- Provide intelligent feedback loop from failures
- Avoid wasting LLM calls on unrepairable issues
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .experiment import Experiment, ExperimentStatus, CodeModule
from .prompts import PromptContext, build_improvement_prompt
from .validator import ValidationReport, Issue, IssueSeverity, IssueCategory


@dataclass
class RetryConfig:
    """Configuration for retry strategy."""
    max_retries: int = 3
    enable_syntax_refinement: bool = True
    enable_type_refinement: bool = True
    enable_import_refinement: bool = True
    verbose: bool = False


@dataclass
class RetryAttempt:
    """Record of a single retry attempt."""
    attempt_number: int
    failure_reason: str
    refined_prompt: str
    result: Optional[Experiment] = None
    success: bool = False


@dataclass
class RetryResult:
    """Result of retry strategy execution."""
    success: bool
    experiment: Optional[Experiment] = None
    attempts: list[RetryAttempt] = None  # type: ignore
    total_attempts: int = 0
    failure_category: Optional[str] = None

    def __post_init__(self) -> None:
        if self.attempts is None:
            self.attempts = []


class RetryStrategy:
    """
    Retry failed experiments with refined prompts.

    Learns from failure and adjusts approach based on error category:
    - Syntax errors: Add bracket/quote validation constraints
    - Type errors: Emphasize type annotation requirements
    - Import errors: Require complete import blocks
    - Generic errors: Provide specific error details in prompt

    Morphism (conceptually): FailedExperiment × PromptContext → Experiment | None
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry strategy with configuration."""
        self.config = config or RetryConfig()

    def should_retry(
        self,
        experiment: Experiment,
        validation_report: Optional[ValidationReport] = None
    ) -> bool:
        """
        Determine if an experiment is worth retrying.

        Skip retry if:
        - Fundamental syntax errors (AST parse failure)
        - Too many validation issues (>10 errors)
        - Module has blocking pre-existing issues
        """
        if experiment.status == ExperimentStatus.PASSED:
            return False

        if not validation_report:
            return True  # Unknown failure, worth retrying

        # Count critical issues
        critical_issues = [
            i for i in validation_report.issues
            if i.severity == IssueSeverity.ERROR
        ]

        # Too many errors suggests fundamental problem
        if len(critical_issues) > 10:
            return False

        # Check for repairable issue types
        repairable_categories = {
            IssueCategory.IMPORT,
            IssueCategory.GENERIC_TYPE,
            IssueCategory.CONSTRUCTOR,
            IssueCategory.TYPE_ANNOTATION,
            IssueCategory.COMPLETENESS,
        }

        has_repairable = any(
            i.category in repairable_categories
            for i in validation_report.issues
        )

        return has_repairable

    def categorize_failure(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport] = None
    ) -> str:
        """
        Categorize failure type for targeted refinement.

        Categories:
        - syntax: Parse/AST errors
        - type: Type annotation issues
        - import: Missing/incorrect imports
        - constructor: Missing or incomplete constructors
        - incomplete: TODO/pass/incomplete code
        - test: Test failures
        - unknown: Other failures
        """
        reason_lower = failure_reason.lower()

        # Check validation report first (more reliable)
        if validation_report and validation_report.issues:
            issue_categories = {i.category for i in validation_report.issues}

            if IssueCategory.IMPORT in issue_categories:
                return "import"
            if IssueCategory.GENERIC_TYPE in issue_categories or IssueCategory.TYPE_ANNOTATION in issue_categories:
                return "type"
            if IssueCategory.CONSTRUCTOR in issue_categories:
                return "constructor"
            if IssueCategory.COMPLETENESS in issue_categories:
                return "incomplete"

        # Fallback to text-based categorization
        if "syntax" in reason_lower or "parse" in reason_lower:
            return "syntax"
        if "type" in reason_lower or "generic" in reason_lower or "annotation" in reason_lower:
            return "type"
        if "import" in reason_lower:
            return "import"
        if "constructor" in reason_lower or "__init__" in reason_lower:
            return "constructor"
        if "test" in reason_lower or "pytest" in reason_lower:
            return "test"
        if "todo" in reason_lower or "pass" in reason_lower or "incomplete" in reason_lower:
            return "incomplete"

        return "unknown"

    def refine_prompt(
        self,
        original_hypothesis: str,
        failure_reason: str,
        attempt: int,
        context: PromptContext,
        validation_report: Optional[ValidationReport] = None
    ) -> str:
        """
        Refine prompt based on failure reason.

        Adds targeted constraints and examples based on:
        - Failure category
        - Specific error details from validation
        - Attempt number (increasing specificity)
        """
        category = self.categorize_failure(failure_reason, validation_report)

        # Build category-specific constraints
        if category == "syntax" and self.config.enable_syntax_refinement:
            constraint = self._syntax_constraint(failure_reason, validation_report)
        elif category == "type" and self.config.enable_type_refinement:
            constraint = self._type_constraint(failure_reason, validation_report)
        elif category == "import" and self.config.enable_import_refinement:
            constraint = self._import_constraint(failure_reason, validation_report)
        elif category == "constructor":
            constraint = self._constructor_constraint(failure_reason, validation_report)
        elif category == "incomplete":
            constraint = self._incomplete_constraint(failure_reason, validation_report)
        else:
            constraint = self._generic_constraint(failure_reason, validation_report)

        # Build refined prompt
        base_prompt = build_improvement_prompt(
            original_hypothesis,
            context,
            improvement_type="retry"
        )

        retry_section = f"""
## ⚠️ RETRY ATTEMPT {attempt + 1}/{self.config.max_retries}

**Previous attempt FAILED. You must fix these issues.**

{constraint}

### Error Details
```
{failure_reason}
```

### Critical Requirements (MUST FOLLOW)
1. Read the error details above carefully
2. Address the specific issues mentioned
3. Validate your code before returning (mentally check syntax/types)
4. Return COMPLETE, WORKING code (not fragments or TODOs)
5. Preserve all existing functionality

**This is retry #{attempt + 1}. Make sure to fix the issues this time.**
"""

        return retry_section + "\n\n" + base_prompt

    def _syntax_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate constraints for syntax errors."""
        return """
**CRITICAL: Previous attempt had SYNTAX ERRORS**

Common syntax issues to avoid:
- Unclosed brackets/parentheses/quotes
- Missing colons after function/class definitions
- Incorrect indentation
- Invalid Python syntax

**Validation checklist before returning code:**
✓ All opening brackets [ ( { have matching closing brackets ] ) }
✓ All strings are properly quoted (single, double, triple quotes)
✓ All function/class definitions end with :
✓ Indentation is consistent (4 spaces)
✓ No placeholder code (TODO, pass, ...)
✓ Code is syntactically valid Python
"""

    def _type_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate constraints for type errors."""
        specific_issues = ""
        if validation_report:
            type_issues = [
                i for i in validation_report.issues
                if i.category in [IssueCategory.GENERIC_TYPE, IssueCategory.TYPE_ANNOTATION]
            ]
            if type_issues:
                specific_issues = "\n**Specific type issues found:**\n"
                for issue in type_issues[:5]:  # Limit to 5 most relevant
                    specific_issues += f"- Line {issue.line}: {issue.message}\n"

        return f"""
**CRITICAL: Previous attempt had TYPE ERRORS**

{specific_issues}

**Type annotation requirements:**
✓ ALL function parameters must have type annotations
✓ ALL function return types must be annotated
✓ Generic types must have correct parameter counts:
  - Agent[Input, Output] (2 params)
  - Maybe[T] (1 param)
  - Fix[A] (1 param)
  - Result[T] (1 param)
✓ Complete all generic brackets: Maybe[str], not Maybe[str
✓ Use proper imports for types (from typing import ...)
✓ Preserve existing type signatures exactly

**Double-check all type annotations before returning.**
"""

    def _import_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate constraints for import errors."""
        return """
**CRITICAL: Previous attempt had MISSING IMPORTS**

**Import requirements:**
✓ Include ALL necessary imports at the top of the file
✓ Copy all imports from the original code
✓ Add new imports for any new symbols used
✓ Use absolute imports: from module import Symbol
✓ Group imports properly:
  1. Standard library
  2. Third-party
  3. Local imports
✓ Verify imported names match their usage in code

**Do not assume any imports - explicitly include them all.**
"""

    def _constructor_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate constraints for constructor errors."""
        return """
**CRITICAL: Previous attempt had CONSTRUCTOR ERRORS**

**Constructor requirements:**
✓ All classes must have EITHER:
  - @dataclass decorator with properly typed fields, OR
  - __init__ method with complete implementation
✓ All dataclass fields must have type annotations
✓ Required fields must come before optional fields
✓ Optional fields should have default values or use Optional[T]
✓ Constructor parameters must match class usage

**Example correct patterns:**
```python
@dataclass
class Foo:
    required_field: str
    optional_field: int = 0

# OR

class Bar:
    def __init__(self, required: str, optional: int = 0):
        self.required = required
        self.optional = optional
```
"""

    def _incomplete_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate constraints for incomplete code."""
        return """
**CRITICAL: Previous attempt had INCOMPLETE CODE**

**Completeness requirements:**
✓ NO placeholder TODO comments
✓ NO empty pass statements (except in abstract methods)
✓ ALL functions must have complete implementations
✓ NO ellipsis (...) placeholders
✓ Return COMPLETE file with ALL code implemented

**This must be production-ready code, not a draft.**
"""

    def _generic_constraint(
        self,
        failure_reason: str,
        validation_report: Optional[ValidationReport]
    ) -> str:
        """Generate generic constraints for unknown failures."""
        return f"""
**CRITICAL: Previous attempt FAILED validation**

**Address this specific issue:**
{failure_reason}

**General requirements:**
✓ Read the error message carefully
✓ Fix the exact issue mentioned
✓ Preserve all other working code
✓ Return complete, valid Python code
✓ Test your changes mentally before returning
"""


# Singleton instance
retry_strategy = RetryStrategy()
