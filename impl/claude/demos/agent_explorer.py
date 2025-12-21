# mypy: ignore-errors
"""
kgents Agent Explorer — Interactive marimo notebook

This notebook demonstrates the MarimoProjector by letting you explore
agents with different capabilities interactively.

Run with:
    cd impl/claude
    marimo edit demos/agent_explorer.py

Or run directly:
    marimo run demos/agent_explorer.py
"""

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import asyncio
    import time
    from dataclasses import dataclass
    from typing import TypeVar, Generic, Any
    from abc import ABC, abstractmethod
    return ABC, Generic, TypeVar, abstractmethod, mo, time


@app.cell
def _(ABC, Generic, TypeVar, abstractmethod):
    # Minimal agent runtime
    A = TypeVar("A")
    B = TypeVar("B")

    class Agent(ABC, Generic[A, B]):
        @property
        @abstractmethod
        def name(self) -> str:
            ...

        @abstractmethod
        async def invoke(self, input: A) -> B:
            ...
    return (Agent,)


@app.cell
def _(Agent):
    # Example agents with different capabilities

    class TextTransformer(Agent[str, str]):
        """Plain agent — transforms text to uppercase."""

        @property
        def name(self) -> str:
            return "text-transformer"

        async def invoke(self, text: str) -> str:
            return text.upper()

    class ReverseAgent(Agent[str, str]):
        """Reverses the input text."""

        @property
        def name(self) -> str:
            return "reverse-agent"

        async def invoke(self, text: str) -> str:
            return text[::-1]

    class WordCountAgent(Agent[str, str]):
        """Counts words in input."""

        @property
        def name(self) -> str:
            return "word-counter"

        async def invoke(self, text: str) -> str:
            words = text.split()
            return f"Word count: {len(words)}\nWords: {', '.join(words)}"

    class EchoAgent(Agent[str, str]):
        """Echoes input with decoration."""

        @property
        def name(self) -> str:
            return "echo-agent"

        async def invoke(self, text: str) -> str:
            return f"🔊 {text} 🔊"
    return EchoAgent, ReverseAgent, TextTransformer, WordCountAgent


@app.cell
def _(mo):
    mo.md("""
    # 🎭 kgents Agent Explorer

    This notebook demonstrates the **MarimoProjector** — one of six projection
    targets in the Alethic Architecture:

    | Projector | Output |
    |-----------|--------|
    | LocalProjector | Runnable Python object |
    | K8sProjector | Kubernetes manifests |
    | CLIProjector | Shell script |
    | DockerProjector | Dockerfile |
    | WASMProjector | Browser sandbox (Pyodide) |
    | **MarimoProjector** | **Interactive notebook cell** ← you are here |

    ---
    """)
    return


@app.cell
def _(EchoAgent, ReverseAgent, TextTransformer, WordCountAgent, mo):
    # Agent selection
    agent_options = {
        "🔠 Text Transformer (uppercase)": TextTransformer,
        "🔄 Reverse Agent (backwards)": ReverseAgent,
        "📊 Word Counter": WordCountAgent,
        "🔊 Echo Agent": EchoAgent,
    }

    agent_selector = mo.ui.dropdown(
        options=agent_options,
        value="🔠 Text Transformer (uppercase)",
        label="Select Agent",
    )
    return (agent_selector,)


@app.cell
def _(agent_selector, mo):
    mo.hstack(
        [
            mo.md("## Choose an Agent"),
            agent_selector,
        ],
        justify="start",
        gap=2,
    )
    return


@app.cell
def _(agent_selector, mo):
    # Get selected agent info
    selected_agent = agent_selector.value
    if selected_agent:
        agent_doc = selected_agent.__doc__ or "No description available."
        mo.callout(mo.md(f"**{selected_agent.__name__}**: {agent_doc}"), kind="info")
    return (selected_agent,)


@app.cell
def _(mo):
    # Input widget
    user_input = mo.ui.text_area(
        placeholder="Enter text to process...",
        label="Input",
        full_width=True,
    )
    return (user_input,)


@app.cell
def _(mo, user_input):
    mo.vstack(
        [
            mo.md("## Input"),
            user_input,
        ]
    )
    return


@app.cell
def _(mo):
    # Run button
    run_button = mo.ui.run_button(label="🚀 Run Agent")
    return (run_button,)


@app.cell
def _(mo, run_button):
    mo.hstack([run_button], justify="center")
    return


@app.cell
async def _(mo, run_button, selected_agent, time, user_input):
    # Execute agent and display results
    async def _run_agent():
        if not user_input.value.strip():
            return mo.callout(mo.md("Please enter some input text."), kind="warn")

        if not selected_agent:
            return mo.callout(mo.md("Please select an agent."), kind="warn")

        start_time = time.time()
        try:
            agent = selected_agent()
            result = await agent.invoke(user_input.value)
            elapsed = (time.time() - start_time) * 1000

            return mo.vstack(
                [
                    mo.md("## Result"),
                    mo.md(f"```\n{result}\n```"),
                    mo.callout(
                        mo.md(f"⏱️ Latency: {elapsed:.2f}ms | Agent: **{agent.name}**"),
                        kind="success",
                    ),
                ]
            )
        except Exception as e:
            return mo.callout(mo.md(f"Error: {e}"), kind="danger")

    if run_button.value:
        await _run_agent()
    else:
        mo.md("*Click 'Run Agent' to execute*")
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## How This Works

    The `MarimoProjector` compiles agent **Halos** (capability declarations) into
    marimo cells. Each capability maps to a marimo feature:

    | Capability | Marimo Feature |
    |------------|----------------|
    | `@Stateful` | `mo.state()` for persistence |
    | `@Soulful` | Persona badge via `mo.callout()` |
    | `@Observable` | Latency metrics display |
    | `@Streamable` | Progress bar indicators |

    This notebook is a **working example** of what `MarimoProjector.compile()` produces.

    ---

    *Built with the Alethic Architecture — same Halo, different projections.*
    """)
    return


if __name__ == "__main__":
    app.run()
