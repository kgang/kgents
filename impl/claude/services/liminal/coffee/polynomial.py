"""
Morning Coffee Polynomial: State machine for the liminal transition ritual.

The Coffee polynomial models the ritual as a state machine:
- Positions: {DORMANT, GARDEN, WEATHER, MENU, CAPTURE, TRANSITION}
- Directions: Valid commands at each position
- Transition: State × Command → (NewState, Output)

Key Design Principles:
1. Every movement is skippable (ritual serves human, not vice versa)
2. Exit is always available (no guilt, no nagging)
3. Garden/Weather are observation-only (non-demanding)
4. Menu presents invitations, not assignments

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

from .types import (
    MOVEMENTS,
    ChallengeMenu,
    CoffeeOutput,
    CoffeeState,
    ConceptualWeather,
    GardenView,
    MenuItem,
    MorningVoice,
    Movement,
    RitualEvent,
)

# =============================================================================
# Direction Functions (Valid Commands per State)
# =============================================================================


def coffee_directions(state: CoffeeState) -> FrozenSet[Any]:
    """
    Valid commands for each Coffee state.

    Law: "exit" is valid in every state (exit honored).
    Law: "skip" is valid in every non-DORMANT state (skippable movements).
    """
    base_cmds: frozenset[str] = frozenset({"exit", "manifest"})

    match state:
        case CoffeeState.DORMANT:
            # Can only wake up or force-start
            return base_cmds | frozenset({"wake", "force_start"})

        case CoffeeState.GARDEN:
            # Observe, continue to weather, skip ahead, or exit
            return base_cmds | frozenset({"continue", "skip_to_menu", "skip"})

        case CoffeeState.WEATHER:
            # Observe, continue to menu, skip ahead, or exit
            return base_cmds | frozenset({"continue", "skip_to_menu", "skip"})

        case CoffeeState.MENU:
            # Select a challenge level, go serendipitous, or exit
            return base_cmds | frozenset({"select", "serendipity", "skip"})

        case CoffeeState.CAPTURE:
            # Record voice, skip capture, or exit
            return base_cmds | frozenset({"record", "skip"})

        case CoffeeState.TRANSITION:
            # Begin work or linger a moment
            return base_cmds | frozenset({"begin_work", "linger"})

    # Fallback (should not reach)
    return base_cmds


# =============================================================================
# Transition Function
# =============================================================================


def coffee_transition(
    state: CoffeeState,
    input: Any,
) -> tuple[CoffeeState, CoffeeOutput]:
    """
    Coffee state transition function.

    transition: State × Input → (NewState, Output)

    This is the heart of the Morning Coffee polynomial.
    Each state handles its valid commands and produces appropriate output.
    """
    # Extract command from input
    cmd = _extract_command(input)
    data = _extract_data(input)

    # Universal commands (valid in all states)
    if cmd == "exit":
        return CoffeeState.DORMANT, CoffeeOutput(
            status="exited",
            state=CoffeeState.DORMANT,
            message="Ritual exited. No guilt, no nagging.",
        )

    if cmd == "manifest":
        movement = _get_current_movement(state)
        return state, CoffeeOutput(
            status="ok",
            state=state,
            movement=movement,
            message=f"Current state: {state.name}",
        )

    # State-specific transitions
    match state:
        case CoffeeState.DORMANT:
            return _handle_dormant(cmd, data)

        case CoffeeState.GARDEN:
            return _handle_garden(cmd, data)

        case CoffeeState.WEATHER:
            return _handle_weather(cmd, data)

        case CoffeeState.MENU:
            return _handle_menu(cmd, data)

        case CoffeeState.CAPTURE:
            return _handle_capture(cmd, data)

        case CoffeeState.TRANSITION:
            return _handle_transition(cmd, data)

    # Fallback
    return state, CoffeeOutput(
        status="error",
        state=state,
        message=f"Unknown command: {cmd}",
    )


# =============================================================================
# State Handlers
# =============================================================================


def _handle_dormant(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle DORMANT state transitions."""
    if cmd in ("wake", "force_start"):
        # Start the ritual, move to Garden
        movement = MOVEMENTS["garden"]
        return CoffeeState.GARDEN, CoffeeOutput(
            status="ok",
            state=CoffeeState.GARDEN,
            movement=movement,
            message=f"☕ {movement.prompt}",
        )

    return CoffeeState.DORMANT, CoffeeOutput(
        status="error",
        state=CoffeeState.DORMANT,
        message=f"Unknown command in DORMANT: {cmd}",
    )


def _handle_garden(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle GARDEN state transitions."""
    # Get garden view from data if provided
    garden = data.get("garden")
    if isinstance(garden, dict):
        # Convert dict to GardenView if needed
        garden = None  # Placeholder: actual conversion in service layer

    if cmd == "continue":
        # Move to Weather
        movement = MOVEMENTS["weather"]
        return CoffeeState.WEATHER, CoffeeOutput(
            status="ok",
            state=CoffeeState.WEATHER,
            movement=movement,
            garden=garden,
            message=f"🌤️ {movement.prompt}",
        )

    if cmd == "skip_to_menu":
        # Skip Weather, go directly to Menu
        movement = MOVEMENTS["menu"]
        return CoffeeState.MENU, CoffeeOutput(
            status="skipped",
            state=CoffeeState.MENU,
            movement=movement,
            garden=garden,
            message=f"⏭️ Skipped to Menu. {movement.prompt}",
        )

    if cmd == "skip":
        # Skip entire ritual (serendipity mode)
        return CoffeeState.TRANSITION, CoffeeOutput(
            status="skipped",
            state=CoffeeState.TRANSITION,
            garden=garden,
            message="⏭️ Inspiration struck! Beginning transition...",
        )

    return CoffeeState.GARDEN, CoffeeOutput(
        status="error",
        state=CoffeeState.GARDEN,
        message=f"Unknown command in GARDEN: {cmd}",
    )


def _handle_weather(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle WEATHER state transitions."""
    weather = data.get("weather")
    if isinstance(weather, dict):
        weather = None  # Placeholder

    if cmd == "continue":
        # Move to Menu
        movement = MOVEMENTS["menu"]
        return CoffeeState.MENU, CoffeeOutput(
            status="ok",
            state=CoffeeState.MENU,
            movement=movement,
            weather=weather,
            message=f"🍳 {movement.prompt}",
        )

    if cmd in ("skip_to_menu", "skip"):
        # Skip to Menu
        movement = MOVEMENTS["menu"]
        return CoffeeState.MENU, CoffeeOutput(
            status="skipped",
            state=CoffeeState.MENU,
            movement=movement,
            weather=weather,
            message=f"⏭️ {movement.prompt}",
        )

    return CoffeeState.WEATHER, CoffeeOutput(
        status="error",
        state=CoffeeState.WEATHER,
        message=f"Unknown command in WEATHER: {cmd}",
    )


def _handle_menu(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle MENU state transitions."""
    menu = data.get("menu")
    if isinstance(menu, dict):
        menu = None  # Placeholder

    if cmd == "select":
        # A challenge was selected, move to Capture
        selection = data.get("selection")
        movement = MOVEMENTS["capture"]
        return CoffeeState.CAPTURE, CoffeeOutput(
            status="ok",
            state=CoffeeState.CAPTURE,
            movement=movement,
            menu=menu,
            message=f"📝 {movement.prompt}",
            data={"selection": selection},
        )

    if cmd == "serendipity":
        # Follow curiosity, move to Capture
        movement = MOVEMENTS["capture"]
        return CoffeeState.CAPTURE, CoffeeOutput(
            status="ok",
            state=CoffeeState.CAPTURE,
            movement=movement,
            menu=menu,
            message=f"🎲 Following curiosity! {movement.prompt}",
            data={"selection": "serendipitous"},
        )

    if cmd == "skip":
        # Skip to Transition
        return CoffeeState.TRANSITION, CoffeeOutput(
            status="skipped",
            state=CoffeeState.TRANSITION,
            menu=menu,
            message="⏭️ Skipping to work...",
        )

    return CoffeeState.MENU, CoffeeOutput(
        status="error",
        state=CoffeeState.MENU,
        message=f"Unknown command in MENU: {cmd}",
    )


def _handle_capture(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle CAPTURE state transitions."""
    if cmd == "record":
        # Record voice capture, move to Transition
        voice_data = data.get("voice", {})
        voice = MorningVoice.from_dict(voice_data) if voice_data else None

        return CoffeeState.TRANSITION, CoffeeOutput(
            status="ok",
            state=CoffeeState.TRANSITION,
            voice=voice,
            message="✨ Voice captured! Ready to begin.",
        )

    if cmd == "skip":
        # Skip capture, move to Transition
        return CoffeeState.TRANSITION, CoffeeOutput(
            status="skipped",
            state=CoffeeState.TRANSITION,
            message="⏭️ Skipping capture. Ready to begin.",
        )

    return CoffeeState.CAPTURE, CoffeeOutput(
        status="error",
        state=CoffeeState.CAPTURE,
        message=f"Unknown command in CAPTURE: {cmd}",
    )


def _handle_transition(cmd: str, data: dict[str, Any]) -> tuple[CoffeeState, CoffeeOutput]:
    """Handle TRANSITION state transitions."""
    if cmd == "begin_work":
        # Complete the ritual
        return CoffeeState.DORMANT, CoffeeOutput(
            status="ok",
            state=CoffeeState.DORMANT,
            message="☀️ Alright, let's begin. The morning is yours.",
        )

    if cmd == "linger":
        # Stay in transition a moment longer
        return CoffeeState.TRANSITION, CoffeeOutput(
            status="ok",
            state=CoffeeState.TRANSITION,
            message="🌅 Taking a moment... the morning waits.",
        )

    return CoffeeState.TRANSITION, CoffeeOutput(
        status="error",
        state=CoffeeState.TRANSITION,
        message=f"Unknown command in TRANSITION: {cmd}",
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _extract_command(input: Any) -> str:
    """Extract command from various input formats."""
    if isinstance(input, str):
        return input
    if isinstance(input, RitualEvent):
        return input.command
    if isinstance(input, dict):
        cmd = input.get("command") or input.get("cmd") or "unknown"
        return str(cmd)
    return "unknown"


def _extract_data(input: Any) -> dict[str, Any]:
    """Extract data from various input formats."""
    if isinstance(input, str):
        return {}
    if isinstance(input, RitualEvent):
        return dict(input.data)
    if isinstance(input, dict):
        return {k: v for k, v in input.items() if k not in ("command", "cmd")}
    return {}


def _get_current_movement(state: CoffeeState) -> Movement | None:
    """Get the Movement for a given state."""
    state_to_movement: dict[CoffeeState, str] = {
        CoffeeState.GARDEN: "garden",
        CoffeeState.WEATHER: "weather",
        CoffeeState.MENU: "menu",
        CoffeeState.CAPTURE: "capture",
    }
    movement_key = state_to_movement.get(state)
    return MOVEMENTS.get(movement_key) if movement_key else None


# =============================================================================
# The Polynomial Agent
# =============================================================================


COFFEE_POLYNOMIAL: PolyAgent[CoffeeState, Any, CoffeeOutput] = PolyAgent(
    name="CoffeePolynomial",
    positions=frozenset(CoffeeState),
    _directions=coffee_directions,
    _transition=coffee_transition,
)
"""
The Morning Coffee polynomial agent.

This maps the ritual to a polynomial state machine:
- positions: 6 states from DORMANT to TRANSITION
- directions: valid commands per state
- transition: command → state change + output

Usage:
    state = CoffeeState.DORMANT
    state, output = COFFEE_POLYNOMIAL.transition(state, "wake")
    # state is now GARDEN, output contains the movement
"""


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "coffee_directions",
    "coffee_transition",
    "COFFEE_POLYNOMIAL",
]
