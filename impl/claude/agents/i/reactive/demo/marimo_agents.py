# mypy: ignore-errors
"""
Reactive Agents Demo - marimo notebook showcasing Wave 11 integration.

Run with: marimo run impl/claude/agents/i/reactive/demo/marimo_agents.py

This notebook demonstrates:
1. AgentCardWidget rendered via anywidget
2. Interactive controls that update widget state
3. AgentTraceWidget for observability
4. Theme customization

Note: This is a marimo notebook. The @app.cell decorator pattern doesn't
play well with strict mypy, hence ignore-errors above.
"""
# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo", "anywidget", "kgents"]
# ///

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Reactive Agents Demo

        This notebook demonstrates kgents reactive widgets rendered in marimo
        via the anywidget protocol (Wave 11 integration).

        The same widget definitions work across:
        - **CLI**: Plain text output
        - **TUI**: Rich/Textual interactive
        - **Notebook**: marimo/Jupyter via anywidget
        """
    )
    return


@app.cell
def _():
    # Import reactive primitives
    from agents.i.reactive.adapters import (
        AgentTraceState,
        AgentTraceWidget,
        MarimoAdapter,
        SpanData,
        create_trace_widget,
        is_anywidget_available,
    )
    from agents.i.reactive.primitives.agent_card import (
        AgentCardState,
        AgentCardWidget,
    )

    return (
        AgentCardWidget,
        AgentCardState,
        MarimoAdapter,
        is_anywidget_available,
        AgentTraceWidget,
        AgentTraceState,
        SpanData,
        create_trace_widget,
    )


@app.cell
def _(mo, is_anywidget_available):
    # Check anywidget availability
    if is_anywidget_available():
        mo.md("**anywidget available** - Full interactive widgets enabled")
    else:
        mo.md("**anywidget not available** - Using HTML fallback")
    return


@app.cell
def _(mo):
    mo.md("## Agent Card Widget")
    return


@app.cell
def _(AgentCardWidget, AgentCardState, MarimoAdapter, mo):
    # Create an agent card
    kgent = AgentCardWidget(
        AgentCardState(
            agent_id="kgent-demo",
            name="Demo Agent",
            phase="active",
            activity=(0.2, 0.4, 0.6, 0.8, 0.6, 0.7, 0.9, 0.5, 0.8, 0.6),
            capability=0.85,
            entropy=0.1,
            breathing=True,
        )
    )

    # Wrap for marimo
    agent_widget = mo.ui.anywidget(MarimoAdapter(kgent))
    agent_widget
    return agent_widget, kgent


@app.cell
def _(mo):
    mo.md("## Interactive Controls")
    return


@app.cell
def _(mo):
    # Phase selector
    phase_select = mo.ui.dropdown(
        options=["idle", "active", "waiting", "complete", "error", "thinking"],
        value="active",
        label="Agent Phase",
    )
    phase_select
    return (phase_select,)


@app.cell
def _(mo):
    # Capability slider
    capability_slider = mo.ui.slider(
        start=0,
        stop=1,
        step=0.05,
        value=0.85,
        label="Capability",
    )
    capability_slider
    return (capability_slider,)


@app.cell
def _(mo):
    # Entropy slider
    entropy_slider = mo.ui.slider(
        start=0,
        stop=1,
        step=0.05,
        value=0.1,
        label="Entropy",
    )
    entropy_slider
    return (entropy_slider,)


@app.cell
def _(
    AgentCardWidget,
    AgentCardState,
    MarimoAdapter,
    mo,
    phase_select,
    capability_slider,
    entropy_slider,
):
    # Reactive agent card that updates based on controls
    reactive_agent = AgentCardWidget(
        AgentCardState(
            agent_id="kgent-reactive",
            name="Reactive Agent",
            phase=phase_select.value,
            activity=(0.3, 0.5, 0.7, 0.6, 0.8, 0.9, 0.7, 0.8),
            capability=capability_slider.value,
            entropy=entropy_slider.value,
            breathing=phase_select.value == "active",
        )
    )

    mo.ui.anywidget(MarimoAdapter(reactive_agent))
    return (reactive_agent,)


@app.cell
def _(mo):
    mo.md("## Agent Trace Widget")
    return


@app.cell
def _(SpanData, create_trace_widget, MarimoAdapter, mo):
    # Create sample trace data
    spans = [
        SpanData(
            span_id="span-1",
            name="agent.run",
            kind="agent",
            start_time_ms=0,
            end_time_ms=1500,
            status="ok",
        ),
        SpanData(
            span_id="span-2",
            name="llm.generate",
            kind="llm_call",
            parent_id="span-1",
            start_time_ms=100,
            end_time_ms=800,
            status="ok",
            attributes={"tokens": 150, "model": "claude-3"},
        ),
        SpanData(
            span_id="span-3",
            name="tool.search",
            kind="tool_use",
            parent_id="span-1",
            start_time_ms=850,
            end_time_ms=1200,
            status="ok",
        ),
        SpanData(
            span_id="span-4",
            name="llm.summarize",
            kind="llm_call",
            parent_id="span-1",
            start_time_ms=1250,
            end_time_ms=1480,
            status="ok",
            attributes={"tokens": 75},
        ),
    ]

    trace_widget = create_trace_widget(
        trace_id="trace-demo-123",
        root_agent="kgent-demo",
        spans=spans,
    )

    mo.ui.anywidget(MarimoAdapter(trace_widget))
    return spans, trace_widget


@app.cell
def _(mo):
    mo.md(
        """
        ## CLI Rendering

        The same widgets can render to plain text for CLI output:
        """
    )
    return


@app.cell
def _(kgent, trace_widget):
    # Show CLI renderings
    print("Agent Card (CLI):")
    print(kgent.to_cli())
    print()
    print("Agent Trace (CLI):")
    print(trace_widget.to_cli())
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## JSON Projection

        Widgets can also project to JSON for API responses:
        """
    )
    return


@app.cell
def _(kgent, mo):
    import json

    mo.md(f"```json\n{json.dumps(kgent.to_json(), indent=2)}\n```")
    return (json,)


if __name__ == "__main__":
    app.run()
