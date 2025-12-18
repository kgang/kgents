"""
Design Polynomial: State machine for UI design state.

The DESIGN_POLYNOMIAL captures mode-dependent UI behavior:
- State: DesignState (density × content_level × motion × should_animate)
- Directions: Available transitions from current state
- Transition: State × Input → State × Output

This enables:
- State-dependent rendering (different UI at different densities)
- Lawful composition (operations verified by DESIGN_OPERAD)
- Observable state changes (for debugging and testing)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from agents.poly import PolyAgent

from .types import ContentLevel, Density, DesignState, MotionType

S = TypeVar("S")
A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Design Inputs
# =============================================================================


@dataclass(frozen=True)
class ViewportResize:
    """Input: viewport dimensions changed."""

    width: int
    height: int


@dataclass(frozen=True)
class ContainerResize:
    """Input: container dimensions changed."""

    width: int


@dataclass(frozen=True)
class AnimationToggle:
    """Input: user toggled animation preference."""

    enabled: bool


@dataclass(frozen=True)
class MotionRequest:
    """Input: request a specific motion type."""

    motion: MotionType


# Union type for all design inputs
DesignInput = ViewportResize | ContainerResize | AnimationToggle | MotionRequest


# =============================================================================
# Design Outputs
# =============================================================================


@dataclass(frozen=True)
class StateChanged:
    """Output: design state was updated."""

    old_state: DesignState
    new_state: DesignState


@dataclass(frozen=True)
class NoChange:
    """Output: input did not change state."""

    state: DesignState


DesignOutput = StateChanged | NoChange


# =============================================================================
# Transition Logic
# =============================================================================


def design_directions(state: DesignState) -> frozenset[Any]:
    """
    Return available input types for current state.

    All inputs are always available (indicated by Any), but some may have no effect.
    The pattern `frozenset({Type, Any})` enables type-based validation while
    allowing the PolyAgent invoke() to accept any matching input.
    """
    return frozenset(
        {
            ViewportResize,
            ContainerResize,
            AnimationToggle,
            MotionRequest,
            Any,  # Universal acceptance marker for PolyAgent protocol
        }
    )


def design_transition(
    state: DesignState, input: DesignInput
) -> tuple[DesignState, DesignOutput]:
    """
    Process a design input and return new state + output.

    This is the core state machine logic.
    """
    match input:
        case ViewportResize(width=w):
            new_density = Density.from_width(w)
            if new_density != state.density:
                new_state = state.with_density(new_density)
                return new_state, StateChanged(state, new_state)
            return state, NoChange(state)

        case ContainerResize(width=w):
            new_level = ContentLevel.from_width(w)
            if new_level != state.content_level:
                new_state = state.with_content_level(new_level)
                return new_state, StateChanged(state, new_state)
            return state, NoChange(state)

        case AnimationToggle(enabled=e):
            if e != state.should_animate:
                new_state = DesignState(
                    density=state.density,
                    content_level=state.content_level,
                    motion=state.motion if e else MotionType.IDENTITY,
                    should_animate=e,
                )
                return new_state, StateChanged(state, new_state)
            return state, NoChange(state)

        case MotionRequest(motion=m):
            # If animations disabled, ignore motion requests (law: !shouldAnimate => identity)
            if not state.should_animate:
                return state, NoChange(state)
            if m != state.motion:
                new_state = state.with_motion(m)
                return new_state, StateChanged(state, new_state)
            return state, NoChange(state)

        case _:
            return state, NoChange(state)


# =============================================================================
# Polynomial Agent
# =============================================================================


def create_design_polynomial(
    initial_state: DesignState | None = None,
) -> PolyAgent[DesignState, DesignInput, DesignOutput]:
    """
    Create a PolyAgent for design state management.

    Usage:
        poly = create_design_polynomial()
        state, output = poly.invoke(initial_state, ViewportResize(375, 667))
    """
    if initial_state is None:
        initial_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.IDENTITY,
            should_animate=True,
        )

    # Create the position set (all reachable states)
    # For design, this is the product of all enum values
    positions: frozenset[DesignState] = frozenset(
        DesignState(
            density=d,
            content_level=c,
            motion=m,
            should_animate=a,
        )
        for d in Density
        for c in ContentLevel
        for m in MotionType
        for a in [True, False]
    )

    return PolyAgent(
        name="DESIGN_POLYNOMIAL",
        positions=positions,
        _directions=design_directions,
        _transition=design_transition,
    )


# Global instance for convenience
DESIGN_POLYNOMIAL = create_design_polynomial()


__all__ = [
    # Input types
    "ViewportResize",
    "ContainerResize",
    "AnimationToggle",
    "MotionRequest",
    "DesignInput",
    # Output types
    "StateChanged",
    "NoChange",
    "DesignOutput",
    # Functions
    "design_directions",
    "design_transition",
    "create_design_polynomial",
    # Instance
    "DESIGN_POLYNOMIAL",
]
