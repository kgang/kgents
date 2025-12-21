import marimo as mo
import asyncio
from dataclasses import dataclass
from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod

# Minimal agent runtime for marimo
A = TypeVar('A')
B = TypeVar('B')

class Agent(ABC, Generic[A, B]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def invoke(self, input: A) -> B: ...

# Agent implementation
class TextTransformer(Agent[str, str]):
    """A simple text transformation agent."""

    @property
    def name(self) -> str:
        return "text-transformer"

    async def invoke(self, text: str) -> str:
        """Transform text to uppercase."""
        return text.upper()


# text-transformer — Interactive Exploration

# Create agent instance
_agent = TextTransformer()

# Input widget
user_input = mo.ui.text_area(
    placeholder="Enter input for the agent...",
    label="Input",
)

# Run button
run_button = mo.ui.run_button(label="Run Agent")

async def run_agent():
    if not user_input.value.strip():
        return mo.callout(mo.md("Please enter some input."), kind="warn")

    try:
        result = await _agent.invoke(user_input.value)

        newline = chr(10)
        latency_callout = None
        return mo.vstack([
            mo.md(f"**Output:**"),
            mo.md(f"```{newline}{result}{newline}```"),
        ] + ([latency_callout] if latency_callout else []))
    except Exception as e:
        return mo.callout(mo.md(f"Error: {e}"), kind="danger")

# Main cell output
mo.vstack([
    mo.hstack([
        mo.md("## text-transformer"),
        mo.md("**Capabilities**: minimal"),
    ]),
    user_input,
    run_button,
    mo.md("---"),
    mo.md("**Output:**") if run_button.value else mo.md("*Click Run to execute*"),
    asyncio.run(run_agent()) if run_button.value else None,
])

# Source viewer
        mo.accordion({
            "View TextTransformer Source": mo.md(f"""
        ```python
        class TextTransformer(Agent[str, str]):
\"\"\"A simple text transformation agent.\"\"\"

@property
def name(self) -> str:
    return "text-transformer"

async def invoke(self, text: str) -> str:
    \"\"\"Transform text to uppercase.\"\"\"
    return text.upper()

        ```
        """)
        })