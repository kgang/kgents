"""
Live Agent Town Orchestration Demo.

The crown jewel demo: live, metered, time-travel-able multi-agent orchestration.

Features:
- Real-time simulation with governed playback
- Isometric factory view + scatter visualization
- Timeline scrubber with time-travel
- Dialogue stream overlay
- Checkpoint-based save/resume

Run with:
    marimo edit agents/town/demo/live_town.py

Or as script:
    marimo run agents/town/demo/live_town.py

See: plans/purring-squishing-duckling.md Phase 6
"""

import marimo

__generated_with = "0.9.20"
app = marimo.App(width="full")


# =============================================================================
# Cell 1: Imports
# =============================================================================


@app.cell
def imports():  # type: ignore[no-untyped-def]
    """Core imports."""
    import marimo as mo

    return (mo,)


@app.cell
def agent_imports():  # type: ignore[no-untyped-def]
    """Import Agent Town components."""
    from agents.town.environment import create_mpp_environment
    from agents.town.flux import TownFlux

    return TownFlux, create_mpp_environment


@app.cell
def dashboard_imports():  # type: ignore[no-untyped-def]
    """Import dashboard components."""
    from agents.town.event_bus import EventBus
    from agents.town.live_dashboard import DashboardLayout, LiveDashboard
    from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig
    from agents.town.trace_bridge import TownTrace

    return (
        DashboardLayout,
        EventBus,
        LiveDashboard,
        PhaseGovernor,
        PhaseTimingConfig,
        TownTrace,
    )


# =============================================================================
# Cell 2: Create Simulation
# =============================================================================


@app.cell
def create_simulation(create_mpp_environment, TownFlux, EventBus):  # type: ignore[no-untyped-def]
    """
    Create the simulation environment.

    This sets up:
    - Town environment with citizens
    - TownFlux for event generation
    - EventBus for fan-out to subscribers
    """
    # Create environment (minimum viable Phase 3)
    env = create_mpp_environment()

    # Create event bus
    event_bus = EventBus()

    # Create flux with event bus wired
    flux = TownFlux(env, seed=42, event_bus=event_bus)

    return env, event_bus, flux


# =============================================================================
# Cell 3: Create Governor
# =============================================================================


@app.cell
def create_governor(flux, PhaseGovernor, PhaseTimingConfig, event_bus):  # type: ignore[no-untyped-def]
    """
    Create phase governor for controlled playback.

    Default: 5 seconds per phase, 1x speed.
    """
    config = PhaseTimingConfig(
        phase_duration_ms=5000,  # 5 seconds per phase
        events_per_phase=5,
        playback_speed=1.0,
        min_event_delay_ms=200,  # Minimum 200ms between events
        max_event_delay_ms=2000,  # Maximum 2s between events
    )

    governor = PhaseGovernor(flux=flux, config=config, event_bus=event_bus)

    return config, governor


# =============================================================================
# Cell 4: Create Dashboard
# =============================================================================


@app.cell
def create_dashboard(flux, governor, LiveDashboard):  # type: ignore[no-untyped-def]
    """
    Create live dashboard composing all widgets.
    """
    dashboard = LiveDashboard.from_flux(flux, governor=governor)

    return (dashboard,)


# =============================================================================
# Cell 5: Playback Controls
# =============================================================================


@app.cell
def playback_controls(mo):  # type: ignore[no-untyped-def]
    """
    Playback control buttons.
    """
    play_button = mo.ui.button(label="Play", kind="success")
    pause_button = mo.ui.button(label="Pause", kind="neutral")
    step_button = mo.ui.button(label="Step", kind="neutral")

    speed_slider = mo.ui.slider(
        start=0.25,
        stop=4.0,
        step=0.25,
        value=1.0,
        label="Speed",
    )

    return pause_button, play_button, speed_slider, step_button


@app.cell
def handle_playback(play_button, pause_button, step_button, speed_slider, dashboard):  # type: ignore[no-untyped-def]
    """
    Handle playback control interactions.
    """
    if play_button.value:
        dashboard.play()
    if pause_button.value:
        dashboard.pause()
    if step_button.value:
        dashboard.step_forward()

    dashboard.set_speed(speed_slider.value)

    return ()


@app.cell
def display_playback_controls(mo, play_button, pause_button, step_button, speed_slider):  # type: ignore[no-untyped-def]
    """Display playback controls."""
    playback_controls_ui = mo.hstack(
        [play_button, pause_button, step_button, mo.md(" | "), speed_slider],
        gap=2,
        justify="start",
    )
    return (playback_controls_ui,)


# =============================================================================
# Cell 6: Layout Controls
# =============================================================================


@app.cell
def layout_controls(mo, DashboardLayout):  # type: ignore[no-untyped-def]
    """
    Layout selection controls.
    """
    layout_select = mo.ui.dropdown(
        options={
            "Full Dashboard": "FULL",
            "Compact": "COMPACT",
            "Minimal": "MINIMAL",
            "Analysis": "ANALYSIS",
        },
        value="Full Dashboard",
        label="Layout",
    )

    return (layout_select,)


@app.cell
def handle_layout(layout_select, dashboard, DashboardLayout):  # type: ignore[no-untyped-def]
    """
    Handle layout selection.
    """
    layout_map = {
        "FULL": DashboardLayout.FULL,
        "COMPACT": DashboardLayout.COMPACT,
        "MINIMAL": DashboardLayout.MINIMAL,
        "ANALYSIS": DashboardLayout.ANALYSIS,
    }
    dashboard.set_layout(layout_map[layout_select.value])

    return ()


# =============================================================================
# Cell 7: Timeline Navigation
# =============================================================================


@app.cell
def timeline_controls(mo):  # type: ignore[no-untyped-def]
    """
    Timeline navigation controls.
    """
    seek_slider = mo.ui.slider(
        start=0,
        stop=100,
        value=0,
        label="Timeline",
    )

    start_button = mo.ui.button(label="Start", kind="neutral")
    end_button = mo.ui.button(label="End", kind="neutral")

    return end_button, seek_slider, start_button


@app.cell
async def handle_timeline(seek_slider, start_button, end_button, dashboard):  # type: ignore[no-untyped-def]
    """
    Handle timeline navigation.
    """
    if start_button.value:
        await dashboard.seek(0)
    if end_button.value:
        if dashboard.timeline:
            await dashboard.seek(dashboard.timeline.max_tick)

    # Seek to slider position (scaled to max_tick)
    if dashboard.timeline and dashboard.timeline.max_tick > 0:
        target_tick = int(seek_slider.value / 100 * dashboard.timeline.max_tick)
        if target_tick != dashboard.current_tick:
            await dashboard.seek(target_tick)

    return ()


@app.cell
def display_timeline_controls(mo, seek_slider, start_button, end_button):  # type: ignore[no-untyped-def]
    """Display timeline controls."""
    timeline_controls_ui = mo.hstack(
        [start_button, seek_slider, end_button],
        gap=2,
        justify="center",
    )
    return (timeline_controls_ui,)


# =============================================================================
# Cell 8: Citizen Selection
# =============================================================================


@app.cell
def citizen_controls(mo, env):  # type: ignore[no-untyped-def]
    """
    Citizen selection controls.
    """
    citizen_names = [c.name for c in env.citizens.values()]

    citizen_select = mo.ui.dropdown(
        options={name: name for name in ["(none)", *citizen_names]},
        value="(none)",
        label="Select Citizen",
    )

    return citizen_names, citizen_select


@app.cell
def handle_citizen_select(citizen_select, dashboard):  # type: ignore[no-untyped-def]
    """
    Handle citizen selection.
    """
    if citizen_select.value == "(none)":
        dashboard.select_citizen(None)
    else:
        dashboard.select_citizen(citizen_select.value)

    return ()


# =============================================================================
# Cell 9: Dashboard Display - Isometric View
# =============================================================================


@app.cell
def display_isometric(mo, dashboard):  # type: ignore[no-untyped-def]
    """
    Display isometric factory view.
    """
    from agents.i.reactive.widget import RenderTarget as _RenderTarget

    if not dashboard.state.panel_visible.get("isometric"):
        isometric_view = mo.md("_Isometric view hidden_")
    elif dashboard.isometric:
        _iso_output = dashboard.isometric.project(_RenderTarget.CLI)
        isometric_view = mo.md(f"```\n{_iso_output}\n```")
    else:
        isometric_view = mo.md("_No isometric data_")

    return (isometric_view,)


# =============================================================================
# Cell 10: Dashboard Display - Scatter View
# =============================================================================


@app.cell
def display_scatter(mo, dashboard):  # type: ignore[no-untyped-def]
    """
    Display scatter visualization.
    """
    from agents.i.reactive.widget import RenderTarget as _ScatterRenderTarget

    if not dashboard.state.panel_visible.get("scatter"):
        scatter_view = mo.md("_Scatter view hidden_")
    elif dashboard.scatter:
        _scatter_output = dashboard.scatter.project(_ScatterRenderTarget.CLI)
        scatter_view = mo.md(f"```\n{_scatter_output}\n```")
    else:
        scatter_view = mo.md("_No scatter data_")

    return (scatter_view,)


# =============================================================================
# Cell 11: Dashboard Display - Timeline
# =============================================================================


@app.cell
def display_timeline(mo, dashboard):  # type: ignore[no-untyped-def]
    """
    Display timeline scrubber.
    """
    if not dashboard.state.panel_visible.get("timeline"):
        timeline_view = mo.md("_Timeline hidden_")
    elif dashboard.timeline:
        _timeline_output = dashboard.timeline.render_cli(width=80)
        timeline_view = mo.md(f"```\n{_timeline_output}\n```")
    else:
        timeline_view = mo.md(f"Tick: {dashboard.current_tick}")

    return (timeline_view,)


# =============================================================================
# Cell 12: Dashboard Display - Dialogue
# =============================================================================


@app.cell
def display_dialogue(mo, dashboard):  # type: ignore[no-untyped-def]
    """
    Display dialogue stream.
    """
    if not dashboard.state.panel_visible.get("dialogue"):
        dialogue_view = mo.md("_Dialogue hidden_")
    else:
        _messages = dashboard.state.dialogue_messages

        if not _messages:
            dialogue_view = mo.md("_No dialogue yet_")
        else:
            _dialogue_lines = []
            for _msg in _messages[-5:]:
                _icon = "monologue" if _msg.is_monologue else "says"
                _dialogue_lines.append(
                    f"**{_msg.speaker_name}** {_icon}: {_msg.message}"
                )

            dialogue_view = mo.vstack([mo.md(line) for line in _dialogue_lines], gap=1)

    return (dialogue_view,)


# =============================================================================
# Cell 13: Status Display
# =============================================================================


@app.cell
def display_status(mo, dashboard, governor):  # type: ignore[no-untyped-def]
    """
    Display current status.
    """
    _state = dashboard.state
    _play_icon = "Playing" if _state.is_playing else "Paused"
    _speed_text = f"{_state.playback_speed}x"

    status_ui = mo.hstack(
        [
            mo.md(f"**Status:** {_play_icon}"),
            mo.md(f"**Speed:** {_speed_text}"),
            mo.md(f"**Phase:** {_state.current_phase}"),
            mo.md(f"**Tick:** {_state.current_tick}"),
            mo.md(f"**Events:** {_state.total_events}"),
            mo.md(f"**Tokens:** {_state.total_tokens}"),
        ],
        gap=4,
    )
    return (status_ui,)


# =============================================================================
# Cell 14: Main Layout
# =============================================================================


@app.cell
def main_layout(  # type: ignore[no-untyped-def]
    mo,
    playback_controls_ui,
    layout_select,
    citizen_select,
    isometric_view,
    scatter_view,
    timeline_controls_ui,
    timeline_view,
    dialogue_view,
    status_ui,
):
    """Main layout combining all components."""
    # The last expression is displayed - no return needed since no cell consumes this
    mo.vstack(
        [
            mo.md("# Live Agent Town Orchestration"),
            mo.hstack(
                [playback_controls_ui, layout_select, citizen_select],
                gap=4,
                justify="space-between",
            ),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md("### Factory View"),
                            isometric_view,
                        ],
                        gap=1,
                    ),
                    mo.vstack(
                        [
                            mo.md("### Personality Space"),
                            scatter_view,
                        ],
                        gap=1,
                    ),
                ],
                gap=4,
            ),
            mo.vstack(
                [
                    mo.md("### Timeline"),
                    timeline_controls_ui,
                    timeline_view,
                ],
                gap=1,
            ),
            mo.vstack(
                [
                    mo.md("### Dialogue"),
                    dialogue_view,
                ],
                gap=1,
            ),
            status_ui,
        ],
        gap=2,
    )


# =============================================================================
# Cell 15: Run Simulation
# =============================================================================


@app.cell
async def run_simulation(mo, dashboard, governor, event_bus):  # type: ignore[no-untyped-def]
    """
    Run the simulation loop.

    This cell runs the governor to generate events.
    Events flow: governor.run() → EventBus → Dashboard
    """
    import asyncio

    # Only run if playing
    if not dashboard.is_playing:
        _sim_result = mo.md("_Simulation paused. Click Play to start._")
    else:
        # Run one phase
        _events_this_run = []
        _error_msg = None
        try:
            async for _event in governor.run(num_phases=1):
                _events_this_run.append(_event)
                # Yield control to allow UI updates
                await asyncio.sleep(0)
        except Exception as _e:
            _error_msg = str(_e)

        if _error_msg:
            _sim_result = mo.md(f"_Error: {_error_msg}_")
        else:
            _sim_result = mo.md(f"_Generated {len(_events_this_run)} events_")

    return (_sim_result,)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    app.run()
