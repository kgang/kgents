"""
Tests for Clarify Tool: Structured Human-in-the-Loop Questions.

Covers:
- Question validation (header length, option count, question format)
- ClarifyTool invocation with valid/invalid requests
- Answer handler injection
- QuestionBuilder fluent API

See: services/tooling/tools/clarify.py
"""

from __future__ import annotations

import pytest

from services.tooling.base import ToolCategory, ToolEffect, ToolError
from services.tooling.contracts import ClarifyRequest
from services.tooling.tools.clarify import (
    ClarifyTool,
    Question,
    QuestionBuilder,
    QuestionOption,
    parse_question,
    reset_answer_handler,
    set_answer_handler,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def clarify_tool() -> ClarifyTool:
    """Fresh ClarifyTool with reset handler."""
    reset_answer_handler()
    yield ClarifyTool()
    reset_answer_handler()


@pytest.fixture
def valid_question_data() -> dict:
    """Valid question data dict."""
    return {
        "header": "Auth",
        "question": "Which auth method?",
        "options": [
            {"label": "OAuth", "description": "Standard OAuth flow"},
            {"label": "JWT", "description": "JSON Web Tokens"},
        ],
        "multiSelect": False,
    }


# =============================================================================
# QuestionOption Tests
# =============================================================================


class TestQuestionOption:
    """Tests for QuestionOption dataclass."""

    def test_create_with_description(self) -> None:
        """Option with description."""
        opt = QuestionOption(label="OAuth", description="Standard flow")
        assert opt.label == "OAuth"
        assert opt.description == "Standard flow"

    def test_create_minimal(self) -> None:
        """Option with just label."""
        opt = QuestionOption(label="OAuth")
        assert opt.label == "OAuth"
        assert opt.description == ""


# =============================================================================
# Question Tests
# =============================================================================


class TestQuestion:
    """Tests for Question validation."""

    def test_valid_question(self) -> None:
        """Valid question passes validation."""
        q = Question(
            header="Auth",
            question="Which auth?",
            options=[
                QuestionOption(label="A"),
                QuestionOption(label="B"),
            ],
        )
        errors = q.validate()
        assert errors == []

    def test_header_too_long(self) -> None:
        """Header exceeding 12 chars fails."""
        q = Question(
            header="Authentication Method",  # 21 chars
            question="Which auth?",
            options=[
                QuestionOption(label="A"),
                QuestionOption(label="B"),
            ],
        )
        errors = q.validate()
        assert any("12 characters" in e for e in errors)

    def test_missing_question_mark(self) -> None:
        """Question without ? fails."""
        q = Question(
            header="Auth",
            question="Which auth",  # No ?
            options=[
                QuestionOption(label="A"),
                QuestionOption(label="B"),
            ],
        )
        errors = q.validate()
        assert any("'?'" in e for e in errors)

    def test_too_few_options(self) -> None:
        """Less than 2 options fails."""
        q = Question(
            header="Auth",
            question="Which auth?",
            options=[QuestionOption(label="A")],
        )
        errors = q.validate()
        assert any("2 options" in e for e in errors)

    def test_too_many_options(self) -> None:
        """More than 4 options fails."""
        q = Question(
            header="Auth",
            question="Which auth?",
            options=[
                QuestionOption(label="A"),
                QuestionOption(label="B"),
                QuestionOption(label="C"),
                QuestionOption(label="D"),
                QuestionOption(label="E"),
            ],
        )
        errors = q.validate()
        assert any("4 options" in e for e in errors)

    def test_empty_option_label(self) -> None:
        """Option with empty label fails."""
        q = Question(
            header="Auth",
            question="Which auth?",
            options=[
                QuestionOption(label=""),
                QuestionOption(label="B"),
            ],
        )
        errors = q.validate()
        assert any("empty label" in e for e in errors)

    def test_multi_select_valid(self) -> None:
        """Multi-select question is valid."""
        q = Question(
            header="Features",
            question="Which features?",
            options=[
                QuestionOption(label="A"),
                QuestionOption(label="B"),
                QuestionOption(label="C"),
            ],
            multi_select=True,
        )
        errors = q.validate()
        assert errors == []


# =============================================================================
# parse_question Tests
# =============================================================================


class TestParseQuestion:
    """Tests for parse_question function."""

    def test_parse_valid(self, valid_question_data: dict) -> None:
        """Parse valid question data."""
        q = parse_question(valid_question_data)
        assert q.header == "Auth"
        assert q.question == "Which auth method?"
        assert len(q.options) == 2
        assert q.options[0].label == "OAuth"
        assert q.multi_select is False

    def test_parse_with_multi_select(self) -> None:
        """Parse question with multiSelect."""
        data = {
            "header": "Features",
            "question": "Which features?",
            "options": [
                {"label": "A", "description": ""},
                {"label": "B", "description": ""},
            ],
            "multiSelect": True,
        }
        q = parse_question(data)
        assert q.multi_select is True

    def test_parse_minimal(self) -> None:
        """Parse minimal question data."""
        data = {
            "header": "Test",
            "question": "Test?",
            "options": [{"label": "A"}, {"label": "B"}],
        }
        q = parse_question(data)
        assert q.header == "Test"
        assert q.options[0].description == ""


# =============================================================================
# ClarifyTool Tests
# =============================================================================


class TestClarifyTool:
    """Tests for ClarifyTool."""

    def test_properties(self, clarify_tool: ClarifyTool) -> None:
        """Tool has correct properties."""
        assert clarify_tool.name == "clarify"
        assert clarify_tool.category == ToolCategory.ORCHESTRATION
        assert clarify_tool.trust_required == 0
        assert (ToolEffect.BLOCKS, "user_input") in clarify_tool.effects

    async def test_invoke_valid_single_question(
        self, clarify_tool: ClarifyTool, valid_question_data: dict
    ) -> None:
        """Invoke with single valid question."""
        request = ClarifyRequest(questions=[valid_question_data])
        response = await clarify_tool.invoke(request)

        assert "Auth" in response.answers
        assert response.answers["Auth"] == "OAuth"  # Default: first option

    async def test_invoke_multiple_questions(self, clarify_tool: ClarifyTool) -> None:
        """Invoke with multiple questions."""
        request = ClarifyRequest(
            questions=[
                {
                    "header": "Auth",
                    "question": "Which auth?",
                    "options": [{"label": "OAuth"}, {"label": "JWT"}],
                },
                {
                    "header": "DB",
                    "question": "Which database?",
                    "options": [{"label": "Postgres"}, {"label": "MySQL"}],
                },
            ]
        )
        response = await clarify_tool.invoke(request)

        assert len(response.answers) == 2
        assert "Auth" in response.answers
        assert "DB" in response.answers

    async def test_invoke_empty_questions(self, clarify_tool: ClarifyTool) -> None:
        """Empty questions list raises error."""
        with pytest.raises(ToolError, match="At least 1 question"):
            await clarify_tool.invoke(ClarifyRequest(questions=[]))

    async def test_invoke_too_many_questions(self, clarify_tool: ClarifyTool) -> None:
        """More than 4 questions raises error."""
        questions = [
            {
                "header": f"Q{i}",
                "question": f"Question {i}?",
                "options": [{"label": "A"}, {"label": "B"}],
            }
            for i in range(5)
        ]
        with pytest.raises(ToolError, match="At most 4 questions"):
            await clarify_tool.invoke(ClarifyRequest(questions=questions))

    async def test_invoke_invalid_question_format(self, clarify_tool: ClarifyTool) -> None:
        """Invalid question format raises error."""
        request = ClarifyRequest(
            questions=[
                {
                    "header": "VeryLongHeaderExceedingLimit",
                    "question": "No question mark",
                    "options": [{"label": "A"}],  # Only 1 option
                }
            ]
        )
        with pytest.raises(ToolError, match="Invalid questions"):
            await clarify_tool.invoke(request)

    async def test_invoke_multi_select(self, clarify_tool: ClarifyTool) -> None:
        """Multi-select question returns comma-separated answers."""
        set_answer_handler(lambda qs: {qs[0].header: ["A", "B"]})

        request = ClarifyRequest(
            questions=[
                {
                    "header": "Features",
                    "question": "Which features?",
                    "options": [{"label": "A"}, {"label": "B"}, {"label": "C"}],
                    "multiSelect": True,
                }
            ]
        )
        response = await clarify_tool.invoke(request)

        assert response.answers["Features"] == "A, B"


# =============================================================================
# Answer Handler Tests
# =============================================================================


class TestAnswerHandler:
    """Tests for pluggable answer handler."""

    async def test_custom_handler(self, clarify_tool: ClarifyTool) -> None:
        """Custom handler provides answers."""
        set_answer_handler(
            lambda qs: {q.header: q.options[1].label for q in qs}  # Select second
        )

        request = ClarifyRequest(
            questions=[
                {
                    "header": "Auth",
                    "question": "Which auth?",
                    "options": [{"label": "OAuth"}, {"label": "JWT"}],
                }
            ]
        )
        response = await clarify_tool.invoke(request)

        assert response.answers["Auth"] == "JWT"

    async def test_handler_receives_parsed_questions(self, clarify_tool: ClarifyTool) -> None:
        """Handler receives parsed Question objects."""
        received: list[Question] = []

        def capture_handler(qs: list[Question]) -> dict[str, str]:
            received.extend(qs)
            return {q.header: q.options[0].label for q in qs}

        set_answer_handler(capture_handler)

        request = ClarifyRequest(
            questions=[
                {
                    "header": "Test",
                    "question": "Test question?",
                    "options": [{"label": "A"}, {"label": "B"}],
                }
            ]
        )
        await clarify_tool.invoke(request)

        assert len(received) == 1
        assert isinstance(received[0], Question)
        assert received[0].header == "Test"


# =============================================================================
# QuestionBuilder Tests
# =============================================================================


class TestQuestionBuilder:
    """Tests for QuestionBuilder fluent API."""

    def test_build_single_question(self) -> None:
        """Build request with single question."""
        request = (
            QuestionBuilder()
            .add("Auth", "Which auth?", [("OAuth", "OAuth flow"), ("JWT", "JWT tokens")])
            .build()
        )

        assert len(request.questions) == 1
        assert request.questions[0]["header"] == "Auth"
        assert len(request.questions[0]["options"]) == 2

    def test_build_multiple_questions(self) -> None:
        """Build request with multiple questions."""
        request = (
            QuestionBuilder()
            .add("Auth", "Which auth?", [("OAuth", ""), ("JWT", "")])
            .add("DB", "Which DB?", [("Postgres", ""), ("MySQL", "")])
            .build()
        )

        assert len(request.questions) == 2
        assert request.questions[0]["header"] == "Auth"
        assert request.questions[1]["header"] == "DB"

    def test_build_with_multi_select(self) -> None:
        """Build request with multi-select question."""
        request = (
            QuestionBuilder()
            .add(
                "Features",
                "Which features?",
                [("A", "Feature A"), ("B", "Feature B")],
                multi_select=True,
            )
            .build()
        )

        assert request.questions[0]["multiSelect"] is True

    async def test_builder_with_clarify_tool(self, clarify_tool: ClarifyTool) -> None:
        """Builder output works with ClarifyTool."""
        request = QuestionBuilder().add("Auth", "Which auth?", [("OAuth", ""), ("JWT", "")]).build()

        response = await clarify_tool.invoke(request)
        assert "Auth" in response.answers


# =============================================================================
# Composition Tests
# =============================================================================


class TestClarifyToolComposition:
    """Tests for clarify tool categorical composition."""

    async def test_compose_with_identity(self, clarify_tool: ClarifyTool) -> None:
        """Clarify tool composes with identity."""
        from services.tooling.base import IdentityTool

        pipeline = IdentityTool[ClarifyRequest]() >> clarify_tool
        assert " >> " in pipeline.name
