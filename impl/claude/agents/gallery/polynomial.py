"""
Gallery Polynomial: State Machine for Gallery Navigation.

The GalleryPolynomial captures the four modes of gallery interaction:
- BROWSING: Viewing the pilot grid, filtering by category
- INSPECTING: Viewing a single pilot's detail
- SIMULATING: Stepping through a polynomial agent's state machine
- VERIFYING: Running operad law checks

See: spec/gallery/gallery-v2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly import PolyAgent


class GalleryPhase(Enum):
    """Gallery navigation phases."""

    BROWSING = auto()  # Viewing pilot grid
    INSPECTING = auto()  # Viewing pilot detail
    SIMULATING = auto()  # Stepping through state machine
    VERIFYING = auto()  # Running law checks


# =============================================================================
# Input Types
# =============================================================================


@dataclass(frozen=True)
class FilterInput:
    """Filter pilots by category."""

    category: str  # "ALL" or category name


@dataclass(frozen=True)
class OverrideInput:
    """Apply rendering overrides."""

    entropy: float | None = None
    seed: int | None = None
    phase: str | None = None


@dataclass(frozen=True)
class SelectPilotInput:
    """Select a pilot for inspection."""

    pilot_name: str


@dataclass(frozen=True)
class CloseInput:
    """Close current panel and return to browsing."""

    pass


@dataclass(frozen=True)
class SimulateInput:
    """Start polynomial simulation for current pilot."""

    pass


@dataclass(frozen=True)
class StepInput:
    """Step the polynomial simulation forward."""

    input_value: Any


@dataclass(frozen=True)
class ResetInput:
    """Reset simulation to initial state."""

    pass


@dataclass(frozen=True)
class VerifyInput:
    """Start operad law verification for current pilot."""

    pass


# =============================================================================
# Output Types
# =============================================================================


@dataclass(frozen=True)
class GalleryOutput:
    """Output from gallery state transitions."""

    message: str
    data: Any = None


# =============================================================================
# State Type
# =============================================================================


@dataclass(frozen=True)
class GalleryState:
    """Full state for gallery polynomial."""

    phase: GalleryPhase
    active_category: str = "ALL"
    selected_pilot: str | None = None
    simulation_state: Any = None
    overrides: OverrideInput | None = None


# =============================================================================
# Transition Logic
# =============================================================================


def _gallery_directions(state: GalleryState) -> FrozenSet[type]:
    """Get valid inputs for current gallery state."""
    match state.phase:
        case GalleryPhase.BROWSING:
            return frozenset([FilterInput, SelectPilotInput, OverrideInput])
        case GalleryPhase.INSPECTING:
            return frozenset([CloseInput, SimulateInput, VerifyInput, OverrideInput])
        case GalleryPhase.SIMULATING:
            return frozenset([StepInput, ResetInput, CloseInput])
        case GalleryPhase.VERIFYING:
            return frozenset([CloseInput])


def _gallery_transition(state: GalleryState, input: Any) -> tuple[GalleryState, GalleryOutput]:
    """Execute gallery state transition."""
    match input:
        case FilterInput(category=cat):
            return (
                GalleryState(
                    phase=GalleryPhase.BROWSING,
                    active_category=cat,
                    selected_pilot=None,
                    overrides=state.overrides,
                ),
                GalleryOutput(f"Filtered to category: {cat}"),
            )

        case SelectPilotInput(pilot_name=name):
            return (
                GalleryState(
                    phase=GalleryPhase.INSPECTING,
                    active_category=state.active_category,
                    selected_pilot=name,
                    overrides=state.overrides,
                ),
                GalleryOutput(f"Inspecting pilot: {name}"),
            )

        case OverrideInput() as ov:
            return (
                GalleryState(
                    phase=state.phase,
                    active_category=state.active_category,
                    selected_pilot=state.selected_pilot,
                    simulation_state=state.simulation_state,
                    overrides=ov,
                ),
                GalleryOutput("Overrides applied", data=ov),
            )

        case CloseInput():
            return (
                GalleryState(
                    phase=GalleryPhase.BROWSING,
                    active_category=state.active_category,
                    selected_pilot=None,
                    overrides=state.overrides,
                ),
                GalleryOutput("Returned to browsing"),
            )

        case SimulateInput():
            return (
                GalleryState(
                    phase=GalleryPhase.SIMULATING,
                    active_category=state.active_category,
                    selected_pilot=state.selected_pilot,
                    simulation_state="initial",  # Would be actual polynomial state
                    overrides=state.overrides,
                ),
                GalleryOutput(f"Started simulation for: {state.selected_pilot}"),
            )

        case StepInput(input_value=val):
            # Would actually step the nested polynomial
            new_sim_state = f"stepped_{val}"
            return (
                GalleryState(
                    phase=GalleryPhase.SIMULATING,
                    active_category=state.active_category,
                    selected_pilot=state.selected_pilot,
                    simulation_state=new_sim_state,
                    overrides=state.overrides,
                ),
                GalleryOutput(f"Stepped with: {val}", data=new_sim_state),
            )

        case ResetInput():
            return (
                GalleryState(
                    phase=GalleryPhase.SIMULATING,
                    active_category=state.active_category,
                    selected_pilot=state.selected_pilot,
                    simulation_state="initial",
                    overrides=state.overrides,
                ),
                GalleryOutput("Simulation reset"),
            )

        case VerifyInput():
            return (
                GalleryState(
                    phase=GalleryPhase.VERIFYING,
                    active_category=state.active_category,
                    selected_pilot=state.selected_pilot,
                    overrides=state.overrides,
                ),
                GalleryOutput(f"Verifying laws for: {state.selected_pilot}"),
            )

        case _:
            raise ValueError(f"Invalid input type: {type(input)}")


# =============================================================================
# Gallery Polynomial
# =============================================================================


# Wrapper for the directions function that works with GalleryState
def _directions_wrapper(state: GalleryState) -> FrozenSet[type]:
    return _gallery_directions(state)


# Wrapper for the transition function
def _transition_wrapper(state: GalleryState, inp: Any) -> tuple[GalleryState, GalleryOutput]:
    return _gallery_transition(state, inp)


# Initial state
GALLERY_INITIAL = GalleryState(phase=GalleryPhase.BROWSING)

# All possible states (simplified - actual states are dynamic)
GALLERY_POSITIONS: FrozenSet[GalleryState] = frozenset(
    [
        GalleryState(phase=GalleryPhase.BROWSING),
        GalleryState(phase=GalleryPhase.INSPECTING),
        GalleryState(phase=GalleryPhase.SIMULATING),
        GalleryState(phase=GalleryPhase.VERIFYING),
    ]
)

GALLERY_POLYNOMIAL: PolyAgent[GalleryState, Any, GalleryOutput] = PolyAgent(
    name="GalleryPolynomial",
    positions=GALLERY_POSITIONS,
    _directions=_directions_wrapper,
    _transition=_transition_wrapper,
)


# =============================================================================
# Visualization Support
# =============================================================================


def gallery_visualization() -> dict[str, Any]:
    """
    Generate visualization data for the gallery polynomial.

    Returns data compatible with PolynomialVisualization type.
    """
    return {
        "id": "gallery",
        "name": "GalleryPolynomial",
        "positions": [
            {
                "id": "BROWSING",
                "label": "Browsing",
                "description": "Viewing pilot grid",
                "icon": "grid-3x3",
                "is_current": True,
                "is_terminal": False,
                "color": "#3b82f6",
            },
            {
                "id": "INSPECTING",
                "label": "Inspecting",
                "description": "Viewing pilot detail",
                "icon": "search",
                "is_current": False,
                "is_terminal": False,
                "color": "#8b5cf6",
            },
            {
                "id": "SIMULATING",
                "label": "Simulating",
                "description": "Stepping through state machine",
                "icon": "play",
                "is_current": False,
                "is_terminal": False,
                "color": "#f59e0b",
            },
            {
                "id": "VERIFYING",
                "label": "Verifying",
                "description": "Running law checks",
                "icon": "check-circle",
                "is_current": False,
                "is_terminal": False,
                "color": "#22c55e",
            },
        ],
        "edges": [
            {
                "source": "BROWSING",
                "target": "INSPECTING",
                "label": "select",
                "is_valid": True,
            },
            {
                "source": "INSPECTING",
                "target": "BROWSING",
                "label": "close",
                "is_valid": True,
            },
            {
                "source": "INSPECTING",
                "target": "SIMULATING",
                "label": "simulate",
                "is_valid": True,
            },
            {
                "source": "INSPECTING",
                "target": "VERIFYING",
                "label": "verify",
                "is_valid": True,
            },
            {
                "source": "SIMULATING",
                "target": "BROWSING",
                "label": "close",
                "is_valid": True,
            },
            {
                "source": "SIMULATING",
                "target": "SIMULATING",
                "label": "step",
                "is_valid": True,
            },
            {
                "source": "VERIFYING",
                "target": "BROWSING",
                "label": "close",
                "is_valid": True,
            },
        ],
        "current": "BROWSING",
        "valid_directions": ["FilterInput", "SelectPilotInput", "OverrideInput"],
        "history": [],
        "metadata": {
            "description": "State machine for gallery navigation",
            "spec": "spec/gallery/gallery-v2.md",
        },
    }


__all__ = [
    # Phase enum
    "GalleryPhase",
    # Input types
    "FilterInput",
    "OverrideInput",
    "SelectPilotInput",
    "CloseInput",
    "SimulateInput",
    "StepInput",
    "ResetInput",
    "VerifyInput",
    # Output types
    "GalleryOutput",
    # State
    "GalleryState",
    "GALLERY_INITIAL",
    # Polynomial
    "GALLERY_POLYNOMIAL",
    # Visualization
    "gallery_visualization",
]
