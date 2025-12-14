"""
kgents Demo Notebook - The Garden Made Visible

This marimo notebook demonstrates the kgents agent ecosystem through
interactive visualizations. The key insight: AGENTESE handles map to
marimo cell reactivity—change an observer, change the world.

Run with: marimo run notebooks/kgents_demo.py
Edit with: marimo edit notebooks/kgents_demo.py
"""

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def __():
    """Imports and setup."""
    import sys
    from pathlib import Path

    import marimo as mo

    # Add impl to path for development
    impl_path = Path(__file__).parent.parent / "impl" / "claude"
    if str(impl_path.parent.parent) not in sys.path:
        sys.path.insert(0, str(impl_path.parent.parent))

    return mo, sys, Path, impl_path


@app.cell
def __(mo):
    """Header and introduction."""
    mo.md(
        """
    # kgents: The Garden Made Visible

    > *"The noun is a lie. There is only the rate of change."*

    This notebook demonstrates the **kgents** agent ecosystem—a specification for
    tasteful, curated, ethical, joy-inducing agents.

    **What you'll see:**
    - **Stigmergic Field**: Agents as currents of cognition, not boxes
    - **Dialectic Engine**: Thesis → Antithesis → Synthesis
    - **Timeline**: The garden's history made scrubable
    - **AGENTESE Handles**: Different observers, different perceptions
    """
    )
    return


@app.cell
def __():
    """Load the core field module."""
    from impl.claude.agents.i.field import (
        EntityType,
        FieldSimulator,
        PheromoneType,
        create_demo_field,
    )

    # Create a demo field with bootstrap agents
    field_state = create_demo_field()

    # Create simulator for dynamics
    simulator = FieldSimulator(field_state)

    return (
        create_demo_field,
        FieldSimulator,
        EntityType,
        PheromoneType,
        field_state,
        simulator,
    )


@app.cell
def __(mo):
    """Section: The Stigmergic Field."""
    mo.md(
        """
    ## The Stigmergic Field

    Agents coordinate through **environmental signals** (pheromones) rather than
    direct communication. Tasks create gravity wells. Contradictions create repulsion.

    **Entities on the field:**
    - `I` - Identity morphism
    - `C` - Compose (function composition)
    - `G` - Ground (reality grounding)
    - `J` - Judge (principle evaluation)
    - `X` - Contradict (tension detection)
    - `S` - Sublate (synthesis engine)
    - `F` - Fix (convergence iterator)
    - `*` - Active task (gravity center)
    - `◊` - Hypothesis (testable idea)
    """
    )
    return


@app.cell
def __(field_state, mo):
    """Create the stigmergic field widget."""
    from impl.claude.agents.i.marimo.widgets import StigmergicFieldWidget

    # Create widget from field state
    raw_field_widget = StigmergicFieldWidget.from_field_state(field_state)

    # Wrap with mo.ui.anywidget for proper marimo integration
    field_widget = mo.ui.anywidget(raw_field_widget)

    # Display the widget
    field_widget
    return StigmergicFieldWidget, field_widget, raw_field_widget


@app.cell
def __(mo, raw_field_widget):
    """Field controls."""
    # Create reactive controls
    tick_button = mo.ui.button(label="Advance Tick")
    reset_button = mo.ui.button(label="Reset Field")
    entropy_slider = mo.ui.slider(
        start=0.0,
        stop=1.0,
        step=0.1,
        value=raw_field_widget.entropy,
        label="Entropy",
    )

    mo.hstack([tick_button, reset_button, entropy_slider])
    return tick_button, reset_button, entropy_slider


@app.cell
def __(tick_button, simulator, raw_field_widget, field_state):
    """Handle tick button."""
    if tick_button.value:
        # Advance simulation
        simulator.tick()
        # Update widget
        raw_field_widget.update_from_field_state(field_state)
    return


@app.cell
def __(entropy_slider, raw_field_widget):
    """Handle entropy slider."""
    raw_field_widget.entropy = entropy_slider.value
    return


@app.cell
def __(mo):
    """Section: The Dialectic Engine."""
    mo.md(
        """
    ## The Dialectic Engine

    Every synthesis emerges from thesis and antithesis. The dialectic widget
    shows this process in action:

    1. **Thesis**: An initial proposition
    2. **Antithesis**: A contradiction that challenges it
    3. **Synthesis**: A higher truth that resolves the tension
    """
    )
    return


@app.cell
def __(mo):
    """Create the dialectic widget."""
    from impl.claude.agents.i.marimo.widgets import DialecticWidget

    raw_dialectic = DialecticWidget()

    # Set up an example dialectic
    raw_dialectic.set_thesis(
        "Agents should be purely reactive", source="Traditional architecture"
    )
    raw_dialectic.set_antithesis(
        "Agents need internal state for learning", source="Machine learning"
    )

    # Wrap with mo.ui.anywidget
    dialectic = mo.ui.anywidget(raw_dialectic)
    dialectic
    return DialecticWidget, dialectic, raw_dialectic


@app.cell
def __(mo, dialectic):
    """Dialectic controls."""
    synthesize_button = mo.ui.button(label="⚡ Synthesize")
    reset_dialectic = mo.ui.button(label="🔄 New Dialectic")

    mo.hstack([synthesize_button, reset_dialectic])
    return synthesize_button, reset_dialectic


@app.cell
def __(synthesize_button, raw_dialectic):
    """Handle synthesis."""
    if synthesize_button.value:
        raw_dialectic.set_synthesis(
            "Agents are polynomials: PolyAgent[S, A, B] = state -> (output, next_state)",
            confidence=0.85,
        )
    return


@app.cell
def __(reset_dialectic, raw_dialectic):
    """Handle reset."""
    if reset_dialectic.value:
        raw_dialectic.reset()
    return


@app.cell
def __(mo):
    """Section: The Timeline."""
    mo.md(
        """
    ## The Timeline

    Every action leaves a trace. The timeline widget shows the garden's
    history, making **time.*** visible and scrubable.
    """
    )
    return


@app.cell
def __(field_state, mo):
    """Create the timeline widget."""
    from impl.claude.agents.i.marimo.widgets import TimelineWidget

    _raw_timeline = TimelineWidget.from_field_state(field_state)
    # Wrap with mo.ui.anywidget
    timeline = mo.ui.anywidget(_raw_timeline)
    timeline
    return TimelineWidget, timeline


@app.cell
def __(mo):
    """Section: AGENTESE Handles."""
    mo.md(
        """
    ## AGENTESE Handles

    > *"There is no view from nowhere. Observation is interaction."*

    Different observers see different affordances. Try different AGENTESE handles:

    ```
    world.house.manifest(architect)  → Blueprint
    world.house.manifest(poet)       → Metaphor
    world.house.manifest(economist)  → Appraisal
    ```
    """
    )
    return


@app.cell
def __(mo):
    """AGENTESE explorer."""
    handle_input = mo.ui.text(
        value="world.field.manifest",
        label="AGENTESE Handle",
        placeholder="e.g., world.field.manifest",
    )
    observer_select = mo.ui.dropdown(
        options=["architect", "poet", "economist", "scientist", "artist"],
        value="architect",
        label="Observer",
    )

    mo.hstack([handle_input, observer_select])
    return handle_input, observer_select


@app.cell
def __(mo, handle_input, observer_select, field_state):
    """Execute AGENTESE handle (mock implementation)."""
    # This is a simplified demonstration
    # Full implementation would use logos.invoke()

    handle = handle_input.value
    observer = observer_select.value

    # Mock responses based on observer
    responses = {
        "architect": f"Field topology: {field_state.width}×{field_state.height} grid with {len(field_state.entities)} entities",
        "poet": f"A garden of {len(field_state.entities)} souls, entropy at {field_state.entropy:.0f}%, dancing in {field_state.dialectic_phase.value}",
        "economist": f"Resource allocation: {len(field_state.get_agents())} agents, {len(field_state.get_attractors())} tasks, heat={field_state.heat:.1f}",
        "scientist": f"Simulation tick {field_state.tick}: {field_state.dialectic_phase.value} phase, {len(field_state.pheromones)} active pheromones",
        "artist": f"Colors of cognition: {'█' * int(field_state.entropy / 10)}{'░' * (10 - int(field_state.entropy / 10))} entropy field",
    }

    result = responses.get(observer, "Unknown observer")

    mo.md(
        f"""
    ### Handle: `{handle}`
    **Observer**: {observer}

    **Result**:
    ```
    {result}
    ```
    """
    )
    return handle, observer, responses, result


@app.cell
def __(mo):
    """Footer."""
    mo.md(
        """
    ---

    ## The Ground (Seven Principles)

    1. **Tasteful** — Clear, justified purpose
    2. **Curated** — Quality over quantity
    3. **Ethical** — Augment, don't replace judgment
    4. **Joy-Inducing** — Personality matters
    5. **Composable** — `f >> g` is primary
    6. **Heterarchical** — No fixed hierarchy
    7. **Generative** — Spec compresses; impl follows

    ---

    *"Plans are worthless, but planning is everything." — Eisenhower*
    """
    )
    return


if __name__ == "__main__":
    app.run()
