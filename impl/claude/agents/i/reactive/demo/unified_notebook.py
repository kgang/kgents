# mypy: ignore-errors
"""
Unified Demo Notebook - Wave 12 marimo integration.

Run with: marimo run impl/claude/agents/i/reactive/demo/unified_notebook.py

This notebook demonstrates the functor property:
Same widget definitions render to CLI, TUI, and Notebook targets.

Note: This is a marimo notebook. The @app.cell decorator pattern doesn't
play well with strict mypy, hence ignore-errors above.
"""
# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo", "anywidget"]
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
        # Unified Demo - Wave 12

        This notebook demonstrates the **functor property** of kgents widgets:

        > Same widget definition, different targets, zero rewrites.

        ```
        project : KgentsWidget[S] → Target → Renderable[Target]
        ```

        The same `UnifiedDashboard` renders to:
        - **CLI**: ASCII art strings
        - **TUI**: Textual/Rich widgets
        - **Notebook**: HTML via anywidget
        - **JSON**: Serializable dicts
        """
    )
    return


@app.cell
def _():
    from agents.i.reactive.adapters import MarimoAdapter, is_anywidget_available
    from agents.i.reactive.demo.unified_app import (
        UnifiedDashboard,
        create_sample_dashboard,
    )

    return (
        MarimoAdapter,
        UnifiedDashboard,
        create_sample_dashboard,
        is_anywidget_available,
    )


@app.cell
def _(create_sample_dashboard):
    # Create the sample dashboard
    dashboard = create_sample_dashboard()
    return (dashboard,)


@app.cell
def _(mo):
    mo.md("## Dashboard (Notebook Rendering)")
    return


@app.cell
def _(dashboard, mo):
    # Render as HTML
    html = dashboard.render_marimo_html()
    mo.Html(html)
    return (html,)


@app.cell
def _(mo):
    mo.md("## Individual Widgets via anywidget")
    return


@app.cell
def _(MarimoAdapter, dashboard, is_anywidget_available, mo):
    # Show agents as anywidgets if available
    if is_anywidget_available():
        agent_widgets = [
            mo.ui.anywidget(MarimoAdapter(agent)) for agent in dashboard.agents
        ]
        mo.hstack(agent_widgets)
    else:
        mo.md("*anywidget not available - showing HTML fallback above*")
    return (agent_widgets,)


@app.cell
def _(mo):
    mo.md("## CLI Rendering Comparison")
    return


@app.cell
def _(dashboard):
    # Show CLI output
    print(dashboard.render_cli())
    return


@app.cell
def _(mo):
    mo.md("## JSON Projection")
    return


@app.cell
def _(dashboard, mo):
    import json

    json_output = dashboard.render_json()
    # Truncate for display
    json_str = json.dumps(json_output, indent=2)
    if len(json_str) > 2000:
        json_str = json_str[:2000] + "\n... (truncated)"
    mo.md(f"```json\n{json_str}\n```")
    return json, json_output, json_str


@app.cell
def _(mo):
    mo.md(
        """
        ## The Functor in Action

        | Target | Output Type | Use Case |
        |--------|-------------|----------|
        | CLI | `str` | Terminal output |
        | TUI | `rich.Panel` | Textual apps |
        | Notebook | `HTML` | marimo/Jupyter |
        | JSON | `dict` | API responses |

        All from the same widget definition. Zero rewrites.
        """
    )
    return


if __name__ == "__main__":
    app.run()
