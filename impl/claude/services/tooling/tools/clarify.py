"""
Clarify Tool: Structured Human-in-the-Loop Questions.

Phase 3 of U-gent Tooling: Orchestration tools for workflow coordination.

ClarifyTool enables agents to ask structured questions during execution:
- 1-4 questions per invocation
- 2-4 options per question
- Optional multiSelect for non-mutually-exclusive choices
- Returns answers as a dict mapping question headers to selected options

Key insight from Claude Code (AskUserQuestion):
- Structured questions > free-form prompts
- Constrained choices reduce ambiguity
- multiSelect when options aren't mutually exclusive

Effect: BLOCKS (waits for user input)

See: plans/ugent-tooling-phase3-handoff.md
See: docs/skills/crown-jewel-patterns.md (Pattern 4: Bounded Trace)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from ..base import Tool, ToolCategory, ToolEffect, ToolError
from ..contracts import (
    ClarifyRequest,
    ClarifyResponse,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Question Validation
# =============================================================================


@dataclass
class QuestionOption:
    """A single option for a question."""

    label: str
    description: str = ""


@dataclass
class Question:
    """A structured question with constrained options."""

    header: str  # Short label (max 12 chars)
    question: str  # Full question text
    options: list[QuestionOption]  # 2-4 options
    multi_select: bool = False  # Allow multiple selections

    def validate(self) -> list[str]:
        """
        Validate question structure.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        if len(self.header) > 12:
            errors.append(f"Header '{self.header}' exceeds 12 characters")

        if not self.question:
            errors.append("Question text is required")

        if not self.question.endswith("?"):
            errors.append(f"Question should end with '?': {self.question}")

        if len(self.options) < 2:
            errors.append(f"At least 2 options required, got {len(self.options)}")

        if len(self.options) > 4:
            errors.append(f"At most 4 options allowed, got {len(self.options)}")

        for i, opt in enumerate(self.options):
            if not opt.label:
                errors.append(f"Option {i} has empty label")

        return errors


def parse_question(data: dict[str, Any]) -> Question:
    """
    Parse question from dict (contract format).

    Args:
        data: Question dict from ClarifyRequest

    Returns:
        Parsed Question object

    Raises:
        ToolError: If question format is invalid
    """
    try:
        options = [
            QuestionOption(
                label=opt.get("label", ""),
                description=opt.get("description", ""),
            )
            for opt in data.get("options", [])
        ]

        return Question(
            header=data.get("header", ""),
            question=data.get("question", ""),
            options=options,
            multi_select=data.get("multiSelect", False),
        )
    except Exception as e:
        raise ToolError(f"Invalid question format: {e}", "clarify") from e


# =============================================================================
# Answer Handler (Pluggable)
# =============================================================================

# Type for answer callback
# Takes list of Questions, returns dict of header → answer(s)
AnswerCallback = Callable[[list[Question]], dict[str, str | list[str]]]


def _default_answer_handler(questions: list[Question]) -> dict[str, str | list[str]]:
    """
    Default answer handler (for testing).

    In production, this would:
    1. Present questions to the user
    2. Wait for user selection(s)
    3. Return the selected answers

    Default behavior: selects first option for each question.
    """
    answers: dict[str, str | list[str]] = {}
    for q in questions:
        if q.options:
            if q.multi_select:
                # Default: select first option as list
                answers[q.header] = [q.options[0].label]
            else:
                # Default: select first option
                answers[q.header] = q.options[0].label
    return answers


_answer_handler: AnswerCallback = _default_answer_handler


def set_answer_handler(handler: AnswerCallback) -> None:
    """Set the answer handler (for testing or production wiring)."""
    global _answer_handler
    _answer_handler = handler


def reset_answer_handler() -> None:
    """Reset to default answer handler."""
    global _answer_handler
    _answer_handler = _default_answer_handler


# =============================================================================
# ClarifyTool
# =============================================================================


@dataclass
class ClarifyTool(Tool[ClarifyRequest, ClarifyResponse]):
    """
    Ask structured questions and get user selections.

    Constraints:
    - 1-4 questions per invocation
    - 2-4 options per question
    - Headers max 12 characters
    - Questions must end with '?'

    Trust Level: L0 (facilitates collaboration)
    Effects: BLOCKS (waits for user input)
    """

    @property
    def name(self) -> str:
        return "clarify"

    @property
    def description(self) -> str:
        return "Ask structured questions to clarify requirements"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [(ToolEffect.BLOCKS, "user_input")]

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Collaboration

    async def invoke(self, request: ClarifyRequest) -> ClarifyResponse:
        """
        Present questions and return user answers.

        Args:
            request: ClarifyRequest with list of questions

        Returns:
            ClarifyResponse with answers dict

        Raises:
            ToolError: If questions are invalid
        """
        # Validate question count
        if not request.questions:
            raise ToolError("At least 1 question required", self.name)

        if len(request.questions) > 4:
            raise ToolError(
                f"At most 4 questions allowed, got {len(request.questions)}",
                self.name,
            )

        # Parse and validate questions
        parsed_questions: list[Question] = []
        all_errors: list[str] = []

        for i, q_data in enumerate(request.questions):
            try:
                q = parse_question(q_data)
                errors = q.validate()
                if errors:
                    all_errors.extend([f"Question {i}: {e}" for e in errors])
                else:
                    parsed_questions.append(q)
            except ToolError as e:
                all_errors.append(f"Question {i}: {e}")

        if all_errors:
            raise ToolError(
                "Invalid questions:\n" + "\n".join(all_errors),
                self.name,
            )

        # Get answers from handler
        raw_answers = _answer_handler(parsed_questions)

        # Convert to response format (all answers as strings)
        answers: dict[str, str] = {}
        for header, value in raw_answers.items():
            if isinstance(value, list):
                answers[header] = ", ".join(value)
            else:
                answers[header] = value

        logger.debug(f"Clarify: {len(parsed_questions)} questions → {len(answers)} answers")

        return ClarifyResponse(answers=answers)


# =============================================================================
# Convenience: Typed Question Builder
# =============================================================================


class QuestionBuilder:
    """
    Fluent builder for constructing ClarifyRequest.

    Example:
        request = (
            QuestionBuilder()
            .add("Auth", "Which auth method?",
                 [("OAuth", "Standard OAuth flow"),
                  ("JWT", "JSON Web Tokens")])
            .add("Storage", "Where to store data?",
                 [("Postgres", "SQL database"),
                  ("Redis", "In-memory cache")],
                 multi_select=True)
            .build()
        )
    """

    def __init__(self) -> None:
        self._questions: list[dict[str, Any]] = []

    def add(
        self,
        header: str,
        question: str,
        options: list[tuple[str, str]],
        multi_select: bool = False,
    ) -> "QuestionBuilder":
        """
        Add a question.

        Args:
            header: Short label (max 12 chars)
            question: Full question text (should end with ?)
            options: List of (label, description) tuples
            multi_select: Allow multiple selections

        Returns:
            Self for chaining
        """
        self._questions.append(
            {
                "header": header,
                "question": question,
                "options": [{"label": label, "description": desc} for label, desc in options],
                "multiSelect": multi_select,
            }
        )
        return self

    def build(self) -> ClarifyRequest:
        """Build the ClarifyRequest."""
        return ClarifyRequest(questions=self._questions)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "Question",
    "QuestionOption",
    "parse_question",
    # Handler
    "AnswerCallback",
    "set_answer_handler",
    "reset_answer_handler",
    # Tool
    "ClarifyTool",
    # Builder
    "QuestionBuilder",
]
