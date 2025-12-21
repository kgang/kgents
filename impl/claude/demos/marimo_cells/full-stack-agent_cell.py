import marimo as mo
import asyncio
from dataclasses import dataclass
from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod
import time

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
class FullStackAgent(Agent[str, str]):
    """An agent with all capabilities for comprehensive exploration."""

    @property
    def name(self) -> str:
        return "full-stack-explorer"

    async def invoke(self, query: str) -> str:
        """Process query with full capabilities."""
        return f"✨ Processing: {query}\n→ Result: {query[::-1]} (reversed)"


# State management for full-stack-agent
agent_state, set_agent_state = mo.state({})
run_history, set_run_history = mo.state([])

# full-stack-agent — Interactive Exploration


# Observable metrics
_start_time = None

def start_metrics():
    global _start_time
    _start_time = time.time()

def get_metrics():
    if _start_time is None:
        return {"latency_ms": 0}
    return {"latency_ms": (time.time() - _start_time) * 1000}

            # Create agent instance
            _agent = FullStackAgent()

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
                start_metrics()
                try:
                    result = await _agent.invoke(user_input.value)
                    metrics = get_metrics()

# Update state
set_run_history(lambda h: h + [{
    "input": user_input.value,
    "output": str(result),
    "timestamp": time.time() if 'time' in dir() else 0,
}])

                    newline = chr(10)
                    latency_callout = mo.callout(mo.md('Latency: ' + str(round(metrics['latency_ms'], 2)) + 'ms'), kind='info')
                    return mo.vstack([
                        mo.md(f"**Output:**"),
                        mo.md(f"```{newline}{result}{newline}```"),
                    ] + ([latency_callout] if latency_callout else []))
                except Exception as e:
                    return mo.callout(mo.md(f"Error: {e}"), kind="danger")

            # Main cell output
            mo.vstack([
                mo.hstack([
                    mo.md("## full-stack-agent"),
                    mo.md("**Capabilities**: stateful • observable"),
mo.callout(mo.md("**Persona**: kent"), kind="info"),
                ]),
                user_input,
                run_button,
                mo.md("---"),
                mo.md("**Output:**") if run_button.value else mo.md("*Click Run to execute*"),
                asyncio.run(run_agent()) if run_button.value else None,
            ])

# Source viewer
        mo.accordion({
            "View FullStackAgent Source": mo.md(f"""
        ```python
        class FullStackAgent(Agent[str, str]):
\"\"\"An agent with all capabilities for comprehensive exploration.\"\"\"

@property
def name(self) -> str:
    return "full-stack-explorer"

async def invoke(self, query: str) -> str:
    \"\"\"Process query with full capabilities.\"\"\"
    return f"✨ Processing: {query}\\n→ Result: {query[::-1]} (reversed)"

        ```
        """)
        })