"""Tests for the tutorial engine."""

from __future__ import annotations

import pytest

from ..tutorial import Tutorial, TutorialStep


class TestTutorialStep:
    """Tests for TutorialStep class."""

    def test_step_creation(self) -> None:
        """TutorialStep can be created with required fields."""
        step = TutorialStep(
            title="Test Step",
            code="print('hello')",
            explanation="A simple test.",
        )
        assert step.title == "Test Step"
        assert step.code == "print('hello')"
        assert step.explanation == "A simple test."
        assert step.execute is None
        assert step.next_hint == ""

    def test_step_with_all_fields(self) -> None:
        """TutorialStep accepts all optional fields."""

        async def executor() -> str:
            return "result"

        step = TutorialStep(
            title="Full Step",
            code="x = 1",
            explanation="Sets x.",
            execute=executor,
            next_hint="Try modifying x",
        )
        assert step.title == "Full Step"
        assert step.execute is executor
        assert step.next_hint == "Try modifying x"

    def test_format_code(self) -> None:
        """_format_code adds line numbers and code block markers."""
        step = TutorialStep(
            title="Test",
            code="line1\nline2",
            explanation="Test",
        )
        formatted = step._format_code(step.code)
        assert "```python" in formatted
        assert "```" in formatted
        assert "1" in formatted
        assert "2" in formatted


class TestTutorial:
    """Tests for Tutorial class."""

    def test_tutorial_creation(self) -> None:
        """Tutorial can be created with basic fields."""
        tutorial = Tutorial(
            name="Test Tutorial",
            description="A test tutorial.",
            steps=[
                TutorialStep(
                    title="Step 1",
                    code="x = 1",
                    explanation="Sets x.",
                ),
            ],
        )
        assert tutorial.name == "Test Tutorial"
        assert tutorial.description == "A test tutorial."
        assert len(tutorial.steps) == 1
        assert "complete" in tutorial.completion_message.lower()

    def test_tutorial_custom_completion(self) -> None:
        """Tutorial accepts custom completion message."""
        tutorial = Tutorial(
            name="Test",
            description="Test",
            steps=[],
            completion_message="Custom ending!",
        )
        assert tutorial.completion_message == "Custom ending!"

    def test_tutorial_multiple_steps(self) -> None:
        """Tutorial can have multiple steps."""
        steps = [
            TutorialStep(title=f"Step {i}", code=f"x = {i}", explanation=f"Step {i}")
            for i in range(5)
        ]
        tutorial = Tutorial(
            name="Multi-Step",
            description="Multiple steps",
            steps=steps,
        )
        assert len(tutorial.steps) == 5


class TestTutorialStepShow:
    """Tests for TutorialStep.show() method."""

    @pytest.mark.asyncio
    async def test_show_json_mode(self) -> None:
        """show() in JSON mode outputs JSON without blocking."""
        step = TutorialStep(
            title="JSON Test",
            code="pass",
            explanation="Testing JSON output",
        )
        # JSON mode should return True (continue) without user input
        result = await step.show(1, 1, json_mode=True, ctx=None)
        assert result is True

    @pytest.mark.asyncio
    async def test_show_with_executor(self) -> None:
        """show() executes the executor function if provided."""
        executed = {"called": False}

        async def executor() -> str:
            executed["called"] = True
            return "executed!"

        step = TutorialStep(
            title="Executor Test",
            code="pass",
            explanation="Testing executor",
            execute=executor,
        )
        # JSON mode to avoid input blocking
        await step.show(1, 1, json_mode=True, ctx=None)
        assert executed["called"] is True

    @pytest.mark.asyncio
    async def test_show_executor_error_handling(self) -> None:
        """show() handles executor errors gracefully."""

        async def failing_executor() -> str:
            raise ValueError("Test error")

        step = TutorialStep(
            title="Error Test",
            code="pass",
            explanation="Testing error handling",
            execute=failing_executor,
        )
        # Should not raise, should continue
        result = await step.show(1, 1, json_mode=True, ctx=None)
        assert result is True


class TestTutorialRun:
    """Tests for Tutorial.run() method."""

    @pytest.mark.asyncio
    async def test_run_json_mode(self) -> None:
        """run() in JSON mode completes without blocking."""
        tutorial = Tutorial(
            name="JSON Tutorial",
            description="Testing JSON mode",
            steps=[
                TutorialStep(title="S1", code="x=1", explanation="E1"),
                TutorialStep(title="S2", code="x=2", explanation="E2"),
            ],
        )
        result = await tutorial.run(json_mode=True, ctx=None)
        assert result == 0

    @pytest.mark.asyncio
    async def test_run_empty_tutorial(self) -> None:
        """run() handles empty tutorial gracefully."""
        tutorial = Tutorial(
            name="Empty",
            description="No steps",
            steps=[],
        )
        result = await tutorial.run(json_mode=True, ctx=None)
        assert result == 0
