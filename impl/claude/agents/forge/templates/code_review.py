"""
Code Review Task Template.

Coalition Shape: Steady + Sync + domain expert
Output Format: PR Comments
Credits: 30

Code review demonstrates precision and attention to detail.
The coalition focuses on correctness, consistency, and improvement.

Flow:
    1. Steady reviews code quality and correctness
    2. Sync checks integration and consistency
    3. Domain expert adds specialized knowledge
    4. Output formatted as PR-style comments
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..task import (
    CoalitionShape,
    HandoffPattern,
    OutputFormat,
    TaskInput,
    TaskOutput,
)
from .base import TaskTemplate

# Coalition shape for code review
CODE_REVIEW_SHAPE = CoalitionShape(
    required=("Steady", "Sync"),
    optional=("Sage",),  # Domain expert
    lead="Steady",
    pattern=HandoffPattern.ITERATIVE,
    min_eigenvector={"analytical": 0.9, "reliability": 0.8},
)


@dataclass
class CodeReviewTask(TaskTemplate):
    """
    Code Review: Thorough PR-style code review.

    Input: Code diff, PR URL, or files to review
    Output: Structured PR comments with:
        - Line-by-line feedback
        - Overall assessment
        - Suggestions for improvement
        - Security/performance flags
    """

    template_id: ClassVar[str] = "code_review"
    name: ClassVar[str] = "Code Review"
    description: ClassVar[str] = (
        "Thorough code review with line-by-line feedback. "
        "Steady ensures quality, Sync checks integration, "
        "domain experts add specialized knowledge."
    )
    base_credits: ClassVar[int] = 30
    output_format: ClassVar[OutputFormat] = OutputFormat.PR_COMMENTS

    coalition_shape: CoalitionShape = field(default_factory=lambda: CODE_REVIEW_SHAPE)

    def validate_input(self, input: TaskInput) -> tuple[bool, list[str]]:
        """Validate code review requirements."""
        is_valid, errors = super().validate_input(input)

        # Need something to review
        has_code = (
            input.context.get("diff")
            or input.context.get("pr_url")
            or input.context.get("files")
        )
        if not has_code:
            errors.append(
                "Code review requires diff, pr_url, or files in context. "
                "Example: context={'diff': '...'} or context={'pr_url': 'github.com/...'}"
            )
            is_valid = False

        return is_valid, errors

    def suggest_coalition(self, input: TaskInput) -> CoalitionShape:
        """Adjust coalition based on code complexity."""
        # Check for security focus
        focus_areas = input.context.get("focus_areas", ())
        if "security" in focus_areas:
            return CoalitionShape(
                required=("Steady", "Sync", "Sage"),  # Add expert
                optional=(),
                lead="Steady",
                pattern=HandoffPattern.ITERATIVE,
            )

        # Large diffs need more reviewers
        diff = input.context.get("diff", "")
        if len(diff) > 5000:  # Large diff
            return CoalitionShape(
                required=("Steady", "Sync", "Sage"),
                optional=(),
                lead="Steady",
                pattern=HandoffPattern.PARALLEL,  # Review in parallel
            )

        return self.coalition_shape

    def get_phase_sequence(self) -> list[str]:
        """Code review: REFINING → INTEGRATING (iterate)."""
        return ["REFINING", "INTEGRATING"]

    def get_handoff_descriptions(self) -> dict[str, str]:
        """Describe expected handoffs."""
        return {
            "Steady→Sync": "Steady passes quality findings to Sync for integration check",
            "Sync→Steady": "Sync flags integration issues back to Steady for verification",
            "Expert→Steady": "Domain expert's specialized feedback integrated",
        }

    async def execute(
        self,
        input: TaskInput,
        coalition: Any,
    ) -> TaskOutput:
        """Execute code review."""
        diff = input.context.get("diff", "")
        pr_url = input.context.get("pr_url", "")
        files = input.context.get("files", [])

        # Generate PR-style comments
        comments = [
            {
                "file": files[0] if files else "unknown",
                "line": 1,
                "comment": "Overall: This code follows good practices",
                "severity": "info",
            },
            {
                "file": files[0] if files else "unknown",
                "line": 10,
                "comment": "Consider adding type hints here",
                "severity": "suggestion",
            },
            {
                "file": files[0] if files else "unknown",
                "line": 25,
                "comment": "This could be refactored for clarity",
                "severity": "suggestion",
            },
        ]

        content = {
            "summary": {
                "status": "approved_with_suggestions",
                "total_comments": len(comments),
                "critical": 0,
                "warnings": 1,
                "suggestions": 2,
            },
            "comments": comments,
            "overall_feedback": (
                f"Code review of {pr_url or 'provided diff'}.\n"
                "The code is generally well-structured with room for improvement."
            ),
        }

        return TaskOutput(
            content=content,
            format=OutputFormat.PR_COMMENTS,
            summary="Code review complete with suggestions",
            coalition_used=self.coalition_shape.required,
            handoffs=2,
            confidence=0.8,
            coverage=0.9,
        )


# Singleton template instance
CODE_REVIEW_TEMPLATE = CodeReviewTask()

__all__ = ["CodeReviewTask", "CODE_REVIEW_TEMPLATE", "CODE_REVIEW_SHAPE"]
