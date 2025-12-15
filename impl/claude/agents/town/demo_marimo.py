"""
Agent Town Marimo Demo (Phase 6 DEVELOP).

Interactive marimo notebook for visualizing Agent Town eigenvector scatter.

Run with:
    marimo edit agents/town/demo_marimo.py

Or as script:
    marimo run agents/town/demo_marimo.py

Laws:
- L1: Cells form DAG (no circular dependencies)
- L2: town_select.value change → Cell 5 re-runs → SSE reconnects
- L3: widget.clicked_citizen_id change → details cell re-runs
- L4: All async operations use `await` in cells
"""

from __future__ import annotations

import marimo

__generated_with = "0.9.20"
app = marimo.App(width="medium")


# =============================================================================
# Cell 1: Imports
# =============================================================================


@app.cell
def imports():  # type: ignore[no-untyped-def]
    """Import dependencies."""
    import marimo as mo

    return (mo,)


@app.cell
def widget_imports():  # type: ignore[no-untyped-def]
    """Import widget and visualization components."""
    from agents.i.marimo.widgets.scatter import EigenvectorScatterWidgetMarimo
    from agents.town.visualization import ProjectionMethod

    return EigenvectorScatterWidgetMarimo, ProjectionMethod


# =============================================================================
# Cell 2: API Client
# =============================================================================


@app.cell
async def api_client(mo):  # type: ignore[no-untyped-def]
    """
    API client for town management.

    Provides async functions to interact with the town API.
    """
    from typing import Any

    import httpx

    API_BASE = "http://localhost:8000/v1/town"

    async def fetch_available_towns() -> list[dict[str, Any]]:
        """Fetch list of available towns."""
        # In production, this would call GET /v1/towns
        # For now, return empty list (create towns via POST)
        return []

    async def create_town(name: str | None = None, phase: int = 4) -> dict[str, Any]:
        """Create a new town."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_BASE,
                json={"name": name, "phase": phase},
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

    async def fetch_scatter_data(
        town_id: str, projection: str = "PAIR_WT"
    ) -> dict[str, Any]:
        """Fetch scatter plot data for a town."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/{town_id}/scatter",
                params={"projection": projection, "format": "json"},
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

    async def fetch_citizen_details(
        town_id: str, citizen_name: str, lod: int = 2
    ) -> dict[str, Any]:
        """Fetch details for a specific citizen."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/{town_id}/citizen/{citizen_name}",
                params={"lod": lod},
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

    async def step_simulation(town_id: str, cycles: int = 1) -> dict[str, Any]:
        """Advance simulation by N cycles."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/{town_id}/step",
                json={"cycles": cycles},
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

    return (
        API_BASE,
        create_town,
        fetch_available_towns,
        fetch_citizen_details,
        fetch_scatter_data,
        step_simulation,
    )


# =============================================================================
# Cell 3: Create Widget
# =============================================================================


@app.cell
def create_widget(mo, EigenvectorScatterWidgetMarimo):  # type: ignore[no-untyped-def]
    """
    Create the scatter widget instance.

    Widget wraps in mo.ui.anywidget for marimo reactivity.
    """
    scatter = EigenvectorScatterWidgetMarimo(
        town_id="",
        api_base="/v1/town",
        show_labels=True,
        show_coalition_colors=True,
        animate_transitions=True,
    )

    widget = mo.ui.anywidget(scatter)

    return scatter, widget


# =============================================================================
# Cell 4: Town Controls
# =============================================================================


@app.cell
def town_controls(mo):  # type: ignore[no-untyped-def]
    """
    Town selection and creation controls.
    """
    # Town ID input (enter existing town ID or leave empty)
    town_id_input = mo.ui.text(
        value="",
        label="Town ID",
        placeholder="Enter town ID or create new",
    )

    # Create new town button
    create_button = mo.ui.button(
        label="Create New Town",
        kind="success",
    )

    # Phase selector for new towns
    phase_select = mo.ui.dropdown(
        options={"Phase 3 (10 citizens)": "3", "Phase 4 (25 citizens)": "4"},
        value="4",
        label="Town Size",
    )

    return create_button, phase_select, town_id_input


@app.cell
def display_town_controls(mo, town_id_input, create_button, phase_select):  # type: ignore[no-untyped-def]
    """Display town controls in a horizontal layout."""
    return mo.hstack(
        [town_id_input, phase_select, create_button],
        gap=2,
        justify="start",
    )


# =============================================================================
# Cell 5: Projection Selector
# =============================================================================


@app.cell
def projection_controls(mo, ProjectionMethod):  # type: ignore[no-untyped-def]
    """
    Projection method selector.
    """
    projection_options = {
        "Warmth vs Trust": "PAIR_WT",
        "Curiosity vs Creativity": "PAIR_CC",
        "Patience vs Resilience": "PAIR_PR",
        "Resilience vs Ambition": "PAIR_RA",
        "PCA": "PCA",
        "t-SNE": "TSNE",
    }

    projection_select = mo.ui.dropdown(
        options=projection_options,
        value="PAIR_WT",
        label="Projection",
    )

    return projection_options, projection_select


# =============================================================================
# Cell 6: Filter Controls
# =============================================================================


@app.cell
def filter_controls(mo):  # type: ignore[no-untyped-def]
    """
    Filter controls for scatter plot.
    """
    evolving_only = mo.ui.checkbox(
        value=False,
        label="Show evolving only",
    )

    archetype_filter = mo.ui.multiselect(
        options=["builder", "trader", "healer", "sage", "explorer", "witness"],
        value=[],
        label="Archetypes",
    )

    return archetype_filter, evolving_only


@app.cell
def display_filter_controls(mo, projection_select, evolving_only, archetype_filter):  # type: ignore[no-untyped-def]
    """Display filter controls."""
    return mo.hstack(
        [projection_select, evolving_only, archetype_filter],
        gap=2,
        justify="start",
    )


# =============================================================================
# Cell 7: Create Town Handler
# =============================================================================


@app.cell
async def handle_create_town(  # type: ignore[no-untyped-def]
    create_button,
    phase_select,
    create_town,
    scatter,
    fetch_scatter_data,
):
    """
    Handle town creation.

    When create_button is clicked, creates a new town and loads scatter data.
    """
    town_data = None
    error_msg = None

    if create_button.value:  # Button was clicked
        try:
            town_data = await create_town(phase=int(phase_select.value))
            town_id = town_data["id"]

            # Load initial scatter data
            scatter_data = await fetch_scatter_data(town_id)
            scatter.points = scatter_data.get("points", [])
            scatter.town_id = town_id

        except Exception as e:
            error_msg = str(e)

    return error_msg, town_data


# =============================================================================
# Cell 8: Connect Existing Town
# =============================================================================


@app.cell
async def connect_town(  # type: ignore[no-untyped-def]
    town_id_input,
    scatter,
    fetch_scatter_data,
):
    """
    Connect to existing town when town_id_input changes.

    Law L2: town_select.value change → SSE reconnects
    """
    if town_id_input.value and town_id_input.value != scatter.town_id:
        try:
            scatter_data = await fetch_scatter_data(town_id_input.value)
            scatter.points = scatter_data.get("points", [])
            scatter.town_id = town_id_input.value
        except Exception:
            pass  # Silently fail for invalid town IDs

    return ()


# =============================================================================
# Cell 9: Update Projection
# =============================================================================


@app.cell
def update_projection(projection_select, scatter):  # type: ignore[no-untyped-def]
    """
    Update projection when selector changes.
    """
    scatter.projection = projection_select.value
    return ()


# =============================================================================
# Cell 10: Update Filters
# =============================================================================


@app.cell
def update_filters(evolving_only, archetype_filter, scatter):  # type: ignore[no-untyped-def]
    """
    Update filters when controls change.
    """
    scatter.show_evolving_only = evolving_only.value
    scatter.archetype_filter = list(archetype_filter.value)
    return ()


# =============================================================================
# Cell 11: Display Scatter
# =============================================================================


@app.cell
def display_scatter(mo, widget):  # type: ignore[no-untyped-def]
    """
    Display the scatter widget.

    This cell re-runs when widget state changes.
    """
    return mo.vstack(
        [
            mo.md("## Agent Town Eigenvector Scatter"),
            widget,
        ],
        gap=2,
    )


# =============================================================================
# Cell 12: Citizen Details Panel
# =============================================================================


@app.cell
async def citizen_details(mo, scatter, fetch_citizen_details):  # type: ignore[no-untyped-def]
    """
    Display details for clicked citizen.

    Law L3: widget.clicked_citizen_id change → this cell re-runs
    """
    if not scatter.clicked_citizen_id or not scatter.town_id:
        return mo.md("_Click a citizen to see details_")

    try:
        # Find citizen name from points
        citizen_name = None
        for p in scatter.points:
            if p.get("citizen_id") == scatter.clicked_citizen_id:
                citizen_name = p.get("citizen_name")
                break

        if not citizen_name:
            return mo.md(f"_Citizen {scatter.clicked_citizen_id[:8]} not found_")

        details = await fetch_citizen_details(scatter.town_id, citizen_name, lod=2)
        citizen = details.get("citizen", {})

        # Format eigenvectors
        ev = citizen.get("eigenvectors", {})
        ev_table = mo.ui.table(
            data=[{"dimension": k, "value": f"{v:.3f}"} for k, v in ev.items()],
            label="Eigenvectors",
        )

        return mo.vstack(
            [
                mo.md(f"### {citizen.get('name', 'Unknown')}"),
                mo.md(f"**Archetype:** {citizen.get('archetype', '?')}"),
                mo.md(f"**Region:** {citizen.get('region', '?')}"),
                mo.md(f"**Phase:** {citizen.get('phase', '?')}"),
                ev_table,
            ],
            gap=1,
        )

    except Exception as e:
        return mo.md(f"_Error loading details: {e}_")


# =============================================================================
# Cell 13: Simulation Controls
# =============================================================================


@app.cell
def simulation_controls(mo):  # type: ignore[no-untyped-def]
    """
    Controls for advancing simulation.
    """
    step_button = mo.ui.button(label="Step Simulation", kind="neutral")
    cycles_slider = mo.ui.slider(
        start=1,
        stop=10,
        value=1,
        label="Cycles",
    )

    return cycles_slider, step_button


@app.cell
async def handle_step(  # type: ignore[no-untyped-def]
    step_button,
    cycles_slider,
    scatter,
    step_simulation,
    fetch_scatter_data,
):
    """
    Handle simulation step.
    """
    if step_button.value and scatter.town_id:
        try:
            await step_simulation(scatter.town_id, cycles=cycles_slider.value)
            # Refresh scatter data
            scatter_data = await fetch_scatter_data(scatter.town_id, scatter.projection)
            scatter.points = scatter_data.get("points", [])
        except Exception:
            pass

    return ()


@app.cell
def display_simulation_controls(mo, step_button, cycles_slider):  # type: ignore[no-untyped-def]
    """Display simulation controls."""
    return mo.hstack(
        [cycles_slider, step_button],
        gap=2,
        justify="start",
    )


# =============================================================================
# Cell 14: Status Footer
# =============================================================================


@app.cell
def status_footer(mo, scatter):  # type: ignore[no-untyped-def]
    """
    Status footer with connection info.
    """
    sse_status = "🟢 Connected" if scatter.sse_connected else "🔴 Disconnected"
    town_status = f"Town: {scatter.town_id[:8]}..." if scatter.town_id else "No town"
    points_count = len(scatter.points)

    return mo.md(f"**Status:** {town_status} | {sse_status} | {points_count} citizens")


# =============================================================================
# Main Layout
# =============================================================================


@app.cell
def main_layout(  # type: ignore[no-untyped-def]
    mo,
    display_town_controls,
    display_filter_controls,
    display_scatter,
    citizen_details,
    display_simulation_controls,
    status_footer,
):
    """
    Main layout combining all components.
    """
    return mo.vstack(
        [
            mo.md("# 🏘️ Agent Town Visualization"),
            display_town_controls,
            display_filter_controls,
            mo.hstack(
                [
                    display_scatter,
                    mo.vstack([citizen_details, display_simulation_controls], gap=2),
                ],
                gap=4,
            ),
            status_footer,
        ],
        gap=2,
    )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    app.run()
