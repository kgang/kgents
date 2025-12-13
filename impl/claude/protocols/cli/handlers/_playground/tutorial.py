"""
Tutorial Engine: Step-by-step interactive lessons.

Each tutorial is a sequence of TutorialSteps that:
1. Show code being written
2. Explain the concept
3. Execute and show results
4. Provide next steps
"""

from __future__ import annotations

import asyncio
import sys
import textwrap
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


@dataclass
class TutorialStep:
    """
    A single step in a tutorial.

    Each step has:
    - title: What we're learning
    - code: The code to show/execute
    - explanation: One-sentence explanation
    - execute: Optional async function to run the code
    - next_hint: What to try next
    """

    title: str
    code: str
    explanation: str
    execute: Callable[[], Awaitable[str]] | None = None
    next_hint: str = ""

    async def show(
        self,
        step_num: int,
        total_steps: int,
        json_mode: bool,
        ctx: "InvocationContext | None",
    ) -> bool:
        """
        Display this step and optionally execute code.

        Returns True to continue, False to quit.
        """
        # Format the step
        header = (
            f"\n{'=' * 60}\n Step {step_num}/{total_steps}: {self.title}\n{'=' * 60}"
        )
        code_block = self._format_code(self.code)

        if json_mode:
            import json

            data = {
                "step": step_num,
                "total": total_steps,
                "title": self.title,
                "code": self.code,
                "explanation": self.explanation,
            }
            _emit_output(json.dumps(data), data, ctx)
        else:
            _emit_output(header, {"step": step_num, "title": self.title}, ctx)
            _emit_output(code_block, {"code": self.code}, ctx)
            _emit_output(
                f"\n{self.explanation}", {"explanation": self.explanation}, ctx
            )

        # Execute if provided
        if self.execute:
            _emit_output("\n[Running...]", {"status": "executing"}, ctx)
            try:
                result = await self.execute()
                _emit_output(f"\nOutput:\n{result}", {"output": result}, ctx)
            except Exception as e:
                _emit_output(f"\nError: {e}", {"error": str(e)}, ctx)

        # Show next hint
        if self.next_hint:
            _emit_output(
                f"\n>> Try next: {self.next_hint}", {"hint": self.next_hint}, ctx
            )

        # Wait for user to continue
        if not json_mode:
            try:
                response = (
                    input("\n[Enter to continue, 'q' to quit, 's' to skip] ")
                    .strip()
                    .lower()
                )
                if response == "q":
                    return False
                if response == "s":
                    return True  # Skip but continue
            except (KeyboardInterrupt, EOFError):
                return False

        return True

    def _format_code(self, code: str) -> str:
        """Format code with line numbers and highlighting."""
        lines = textwrap.dedent(code).strip().split("\n")
        formatted = ["\n```python"]
        for i, line in enumerate(lines, 1):
            formatted.append(f"{i:3}  {line}")
        formatted.append("```")
        return "\n".join(formatted)


@dataclass
class Tutorial:
    """
    A complete tutorial with multiple steps.

    Tutorials guide users through concepts progressively,
    building understanding through practice.
    """

    name: str
    description: str
    steps: list[TutorialStep]
    completion_message: str = "Tutorial complete! You now understand the basics."

    async def run(
        self,
        json_mode: bool,
        ctx: "InvocationContext | None",
    ) -> int:
        """Run the complete tutorial."""
        # Show intro
        intro = f"""
{"=" * 60}
 Tutorial: {self.name}
{"=" * 60}

{self.description}

This tutorial has {len(self.steps)} steps.
Press Enter to proceed through each step.
"""
        _emit_output(
            intro,
            {
                "tutorial": self.name,
                "description": self.description,
                "steps": len(self.steps),
            },
            ctx,
        )

        if not json_mode:
            try:
                input("[Press Enter to start]")
            except (KeyboardInterrupt, EOFError):
                return 0

        # Run each step
        for i, step in enumerate(self.steps, 1):
            should_continue = await step.show(i, len(self.steps), json_mode, ctx)
            if not should_continue:
                _emit_output(
                    "\n[Tutorial ended early. Come back anytime!]",
                    {"status": "quit"},
                    ctx,
                )
                return 0

        # Show completion
        completion = f"""
{"=" * 60}
 Completed: {self.name}
{"=" * 60}

{self.completion_message}

What's next?
  - kgents play          # Try another tutorial
  - kgents play repl     # Free exploration
  - kgents soul reflect  # Chat with K-gent
"""
        _emit_output(completion, {"status": "complete", "tutorial": self.name}, ctx)

        return 0


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
