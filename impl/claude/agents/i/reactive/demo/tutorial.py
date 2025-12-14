# mypy: ignore-errors
"""
Reactive Substrate Tutorial - Learn the functor pattern step by step.

Run with: marimo run impl/claude/agents/i/reactive/demo/tutorial.py

This interactive notebook teaches you to:
1. Create widgets from state
2. Render to different targets
3. Compose widgets using slots
4. Use reactive signals for dynamic updates

Each cell builds on the previous one. Run them in order.

Note: This is a marimo notebook. The @app.cell decorator pattern doesn't
play well with strict mypy, hence ignore-errors above.
"""
# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo"]
# ///

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


# =============================================================================
# Part 1: Introduction
# =============================================================================


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Reactive Substrate Tutorial

        Welcome! This tutorial teaches you the **functor pattern** for building
        target-agnostic widgets.

        > **The Key Insight**: Define a widget once, render it anywhere.

        ```
        project : KgentsWidget[S] -> Target -> Renderable[Target]
        ```

        By the end, you'll understand:
        - How widgets separate **state** from **presentation**
        - How the **project()** functor maps to different targets
        - How to **compose** widgets using slots
        - How **reactive signals** enable dynamic updates

        Let's begin!
        """
    )
    return


# =============================================================================
# Part 2: Your First Widget
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 1: Your First Widget

        Every widget has two parts:
        1. **State** - The data (a dataclass)
        2. **Widget** - The renderer (knows how to visualize state)

        Let's create an `AgentCardWidget`:
        """
    )
    return


@app.cell
def _():
    from agents.i.reactive import AgentCardState, AgentCardWidget

    # Step 1: Define state
    my_state = AgentCardState(
        name="Tutorial Agent",
        phase="active",  # 'active', 'waiting', 'idle', 'error'
        activity=(0.3, 0.5, 0.7, 0.9),  # sparkline data
        capability=0.85,  # 0.0 to 1.0
    )

    # Step 2: Create widget from state
    my_widget = AgentCardWidget(my_state)

    return AgentCardState, AgentCardWidget, my_state, my_widget


@app.cell
def _(mo, my_widget):
    mo.md(
        f"""
        ### CLI Output

        The simplest projection is CLI - plain ASCII text:

        ```
        {my_widget.to_cli()}
        ```

        This is what you'd see in a terminal. Let's explore other targets.
        """
    )
    return


# =============================================================================
# Part 3: Multiple Targets
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 2: The Four Targets

        The same widget can render to four targets:

        | Target | Method | Returns | Use Case |
        |--------|--------|---------|----------|
        | CLI | `to_cli()` | `str` | Terminal output |
        | TUI | `to_tui()` | Rich/Textual | Interactive apps |
        | Marimo | `to_marimo()` | HTML | Notebooks |
        | JSON | `to_json()` | `dict` | APIs |

        **Same state. Different projections. Zero rewrites.**
        """
    )
    return


@app.cell
def _(mo, my_widget):
    # Get all four projections
    cli_output = my_widget.to_cli()
    marimo_output = my_widget.to_marimo()
    json_output = my_widget.to_json()

    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("**CLI**"),
                    mo.md(f"```\n{cli_output}\n```"),
                ]
            ),
            mo.vstack(
                [
                    mo.md("**Marimo (HTML)**"),
                    mo.Html(marimo_output),
                ]
            ),
        ],
        justify="start",
        gap=2,
    )
    return cli_output, json_output, marimo_output


@app.cell
def _(json_output, mo):
    import json

    mo.md(
        f"""
        ### JSON Output (for APIs)

        ```json
        {json.dumps(json_output, indent=2)}
        ```
        """
    )
    return (json,)


# =============================================================================
# Part 4: Understanding the Functor
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 3: The Functor Pattern

        Under the hood, `to_cli()`, `to_marimo()`, etc. all call the same method:

        ```python
        def project(self, target: RenderTarget) -> Any:
            match target:
                case RenderTarget.CLI:
                    return self._render_cli()
                case RenderTarget.MARIMO:
                    return self._render_html()
                case RenderTarget.JSON:
                    return self._to_dict()
        ```

        This is a **functor**: a structure-preserving map.

        - Input: Widget + Target
        - Output: Renderable appropriate for that target
        - Guarantee: Same state always produces same output (deterministic)
        """
    )
    return


@app.cell
def _():
    # You can also call project() directly
    from agents.i.reactive import GlyphState, GlyphWidget, RenderTarget

    glyph = GlyphWidget(GlyphState(phase="active", entropy=0.05))

    # These are equivalent:
    cli_via_method = glyph.to_cli()
    cli_via_project = glyph.project(RenderTarget.CLI)

    assert cli_via_method == cli_via_project
    return GlyphState, GlyphWidget, RenderTarget, cli_via_method, cli_via_project, glyph


@app.cell
def _(cli_via_method, mo):
    mo.md(
        f"""
        ### Glyph: The Atomic Unit

        The `GlyphWidget` is the simplest widget - a single character with phase semantics:

        ```
        {cli_via_method}
        ```

        All other widgets compose from glyphs. This is the **Glyph as Atomic Unit** principle.
        """
    )
    return


# =============================================================================
# Part 5: More Widget Types
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 4: Widget Gallery

        The reactive substrate provides several widget types:

        ### Atomic
        - `GlyphWidget` - Single character with phase semantics

        ### Composed
        - `BarWidget` - Progress/capacity bars
        - `SparklineWidget` - Time-series mini-charts
        - `DensityFieldWidget` - 2D spatial visualization

        ### Cards
        - `AgentCardWidget` - Full agent representation
        - `YieldCardWidget` - Function return values
        - `ShadowCardWidget` - H-gent shadow introspection
        - `DialecticCardWidget` - Thesis/antithesis/synthesis
        """
    )
    return


@app.cell
def _():
    from agents.i.reactive import (
        BarState,
        BarWidget,
        SparklineState,
        SparklineWidget,
    )

    # Create a bar widget
    bar = BarWidget(
        BarState(
            value=0.75,
            width=20,
            style="gradient",  # 'solid', 'gradient', 'blocks'
            label="Memory",
        )
    )

    # Create a sparkline widget
    sparkline = SparklineWidget(
        SparklineState(
            values=(0.2, 0.4, 0.6, 0.8, 0.6, 0.9, 0.7, 0.5),
            label="CPU",
            max_length=10,
        )
    )

    return BarState, BarWidget, SparklineState, SparklineWidget, bar, sparkline


@app.cell
def _(bar, mo, sparkline):
    mo.md(
        f"""
        ### BarWidget

        ```
        {bar.to_cli()}
        ```

        ### SparklineWidget

        ```
        {sparkline.to_cli()}
        ```

        Both use the **same pattern**: state defines data, widget defines rendering.
        """
    )
    return


# =============================================================================
# Part 6: Reactive Signals
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 5: Reactive Signals

        For dynamic updates, the reactive substrate provides three primitives:

        | Primitive | Purpose |
        |-----------|---------|
        | `Signal[T]` | Observable state that notifies on change |
        | `Computed[T]` | Derived state (auto-updates when dependencies change) |
        | `Effect` | Side effects triggered by signal changes |

        These enable reactive UIs without manual wiring.
        """
    )
    return


@app.cell
def _():
    from agents.i.reactive import Computed, Effect, Signal

    # Create a signal
    count = Signal.of(0)

    # Create a computed value (doubles the count)
    doubled = count.map(lambda x: x * 2)

    # The signal's value
    initial_count = count.value
    initial_doubled = doubled.value

    return Computed, Effect, Signal, count, doubled, initial_count, initial_doubled


@app.cell
def _(count, doubled, mo):
    mo.md(
        f"""
        ### Signal in Action

        ```python
        count = Signal.of(0)
        doubled = count.map(lambda x: x * 2)
        ```

        Current values:
        - `count.value` = {count.value}
        - `doubled.value` = {doubled.value}

        When `count` changes, `doubled` automatically updates.
        """
    )
    return


@app.cell
def _(count, doubled):
    # Update the signal
    count.set(5)

    updated_count = count.value
    updated_doubled = doubled.value

    return updated_count, updated_doubled


@app.cell
def _(mo, updated_count, updated_doubled):
    mo.md(
        f"""
        After `count.set(5)`:
        - `count.value` = {updated_count}
        - `doubled.value` = {updated_doubled}

        The computed value updated automatically!
        """
    )
    return


# =============================================================================
# Part 7: Widget Composition
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 6: Composition with Slots

        Complex widgets compose simpler ones using **slots**:

        ```python
        class AgentCardWidget(CompositeWidget[AgentCardState]):
            def __init__(self, state):
                super().__init__(state)
                # Fill slots with child widgets
                self.slots["glyph"] = GlyphWidget(...)
                self.slots["sparkline"] = SparklineWidget(...)
                self.slots["bar"] = BarWidget(...)
        ```

        This is the **Slots/Fillers Composition** principle - like operads in mathematics.
        """
    )
    return


@app.cell
def _(AgentCardState, AgentCardWidget, mo):
    # AgentCardWidget composes three sub-widgets
    composed = AgentCardWidget(
        AgentCardState(
            name="Composed Agent",
            phase="waiting",
            activity=(0.1, 0.3, 0.5, 0.7, 0.5),
            capability=0.6,
        )
    )

    # The CLI output shows all three composed elements
    mo.md(
        f"""
        ### Composition in Action

        An `AgentCardWidget` composes:
        - A `GlyphWidget` (phase indicator)
        - A `SparklineWidget` (activity history)
        - A `BarWidget` (capability level)

        ```
        {composed.to_cli()}
        ```
        """
    )
    return (composed,)


# =============================================================================
# Part 8: Building Your Own Widget
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Part 7: Build Your Own Widget

        To create a custom widget:

        1. Define a state dataclass
        2. Subclass `KgentsWidget[YourState]`
        3. Implement `project(target)` method

        ```python
        from dataclasses import dataclass
        from agents.i.reactive import KgentsWidget, RenderTarget

        @dataclass(frozen=True)
        class CounterState:
            value: int
            label: str

        class CounterWidget(KgentsWidget[CounterState]):
            def project(self, target: RenderTarget) -> Any:
                match target:
                    case RenderTarget.CLI:
                        return f"{self.state.value.label}: {self.state.value.value}"
                    case RenderTarget.JSON:
                        return {"label": self.state.value.label, "value": self.state.value.value}
                    case _:
                        return self.project(RenderTarget.CLI)
        ```
        """
    )
    return


# =============================================================================
# Part 9: Summary
# =============================================================================


@app.cell
def _(mo):
    mo.md(
        """
        ## Summary

        You've learned the reactive substrate's core concepts:

        | Concept | What It Does |
        |---------|--------------|
        | **State** | Immutable dataclass holding widget data |
        | **Widget** | Renderer that knows how to visualize state |
        | **project()** | Functor that maps widget to target-specific output |
        | **Targets** | CLI, TUI, Marimo, JSON - same widget, different outputs |
        | **Signals** | Observable state for reactive updates |
        | **Slots** | Composition pattern for complex widgets |

        ### The Six Principles

        1. **Pure Entropy Algebra** - No random.random() in render paths
        2. **Time Flows Downward** - Parent provides t to children
        3. **Projections Are Manifest** - project() IS logos.invoke("manifest")
        4. **Glyph as Atomic Unit** - Everything composes from glyphs
        5. **Deterministic Joy** - Same seed -> same personality, forever
        6. **Slots/Fillers Composition** - Operad-like widget composition

        ### Next Steps

        - Run `kg dashboard --demo` to see widgets in a live TUI
        - Explore `impl/claude/agents/i/reactive/primitives/` for more widgets
        - Read the [README](../README.md) for API reference
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---

        *Built with the Reactive Substrate v1.0.0*

        ```
        pip install kgents
        ```
        """
    )
    return


if __name__ == "__main__":
    app.run()
