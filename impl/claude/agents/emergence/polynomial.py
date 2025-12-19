"""
Emergence Polynomial: State machine for cymatics experience.

The EMERGENCE_POLYNOMIAL captures mode-dependent behavior:
- State: EmergenceState (phase × family × config × circadian × qualia)
- Directions: Available transitions from current phase
- Transition: State × Input → State × Output

Phase Machine:
    IDLE → LOADING → GALLERY ⇌ EXPLORING → EXPORTING
                       ↓
                    GALLERY

See: plans/structured-greeting-boot.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.poly import PolyAgent

from .types import (
    CIRCADIAN_MODIFIERS,
    FAMILY_QUALIA,
    CircadianPhase,
    EmergencePhase,
    EmergenceState,
    PatternConfig,
    PatternFamily,
    QualiaCoords,
)

# =============================================================================
# Emergence Inputs
# =============================================================================


@dataclass(frozen=True)
class SelectFamily:
    """Input: User selected a pattern family."""

    family: PatternFamily


@dataclass(frozen=True)
class SelectPreset:
    """Input: User selected a curated preset."""

    preset_key: str


@dataclass(frozen=True)
class TuneParam:
    """Input: User adjusted a pattern parameter."""

    param_name: str  # "param1", "param2", "hue", "saturation", "speed"
    value: float


@dataclass(frozen=True)
class ApplyConfig:
    """Input: Apply a complete pattern configuration."""

    config: PatternConfig


@dataclass(frozen=True)
class UpdateCircadian:
    """Input: Circadian phase changed (auto or manual)."""

    phase: CircadianPhase


@dataclass(frozen=True)
class StartLoading:
    """Input: Begin loading/computing pattern."""

    pass


@dataclass(frozen=True)
class LoadingComplete:
    """Input: Pattern loading finished."""

    pass


@dataclass(frozen=True)
class EnterGallery:
    """Input: Enter gallery view mode."""

    pass


@dataclass(frozen=True)
class EnterExplore:
    """Input: Enter explore/detail view mode."""

    config: PatternConfig


@dataclass(frozen=True)
class StartExport:
    """Input: Begin export workflow."""

    pass


@dataclass(frozen=True)
class CancelExport:
    """Input: Cancel export and return to exploring."""

    pass


@dataclass(frozen=True)
class CompleteExport:
    """Input: Export completed successfully."""

    pass


@dataclass(frozen=True)
class ReturnToGallery:
    """Input: Return from exploring to gallery."""

    pass


@dataclass(frozen=True)
class Reset:
    """Input: Reset to idle state."""

    pass


# Union type for all emergence inputs
EmergenceInput = (
    SelectFamily
    | SelectPreset
    | TuneParam
    | ApplyConfig
    | UpdateCircadian
    | StartLoading
    | LoadingComplete
    | EnterGallery
    | EnterExplore
    | StartExport
    | CancelExport
    | CompleteExport
    | ReturnToGallery
    | Reset
)


# =============================================================================
# Emergence Outputs
# =============================================================================


@dataclass(frozen=True)
class PhaseChanged:
    """Output: Phase transition occurred."""

    old_phase: EmergencePhase
    new_phase: EmergencePhase


@dataclass(frozen=True)
class FamilyChanged:
    """Output: Selected family changed."""

    family: PatternFamily
    qualia: QualiaCoords


@dataclass(frozen=True)
class ConfigChanged:
    """Output: Pattern configuration updated."""

    config: PatternConfig


@dataclass(frozen=True)
class CircadianChanged:
    """Output: Circadian phase changed."""

    phase: CircadianPhase
    qualia: QualiaCoords


@dataclass(frozen=True)
class ExportReady:
    """Output: Export data is ready."""

    config: PatternConfig
    export_data: dict[str, Any]


@dataclass(frozen=True)
class NoChange:
    """Output: Input did not change state."""

    state: EmergenceState
    reason: str = ""


# Union type for all emergence outputs
EmergenceOutput = (
    PhaseChanged | FamilyChanged | ConfigChanged | CircadianChanged | ExportReady | NoChange
)


# =============================================================================
# Transition Logic
# =============================================================================


def emergence_directions(state: EmergenceState) -> frozenset[type]:
    """
    Return valid input types for current phase.

    This implements the phase machine constraints.
    """
    base_inputs: set[type] = {UpdateCircadian, Reset}

    match state.phase:
        case EmergencePhase.IDLE:
            return frozenset(base_inputs | {StartLoading, EnterGallery, SelectFamily})

        case EmergencePhase.LOADING:
            return frozenset(base_inputs | {LoadingComplete})

        case EmergencePhase.GALLERY:
            return frozenset(
                base_inputs | {SelectFamily, SelectPreset, EnterExplore, ApplyConfig, TuneParam}
            )

        case EmergencePhase.EXPLORING:
            return frozenset(
                base_inputs
                | {
                    TuneParam,
                    ApplyConfig,
                    StartExport,
                    ReturnToGallery,
                    SelectFamily,
                }
            )

        case EmergencePhase.EXPORTING:
            return frozenset(base_inputs | {CancelExport, CompleteExport})

        case _:
            return frozenset(base_inputs)


def emergence_transition(
    state: EmergenceState, input: EmergenceInput
) -> tuple[EmergenceState, EmergenceOutput]:
    """
    Process emergence input and return new state + output.

    This is the core state machine logic.
    """
    match input:
        # Phase transitions
        case StartLoading():
            if state.phase in (EmergencePhase.IDLE, EmergencePhase.GALLERY):
                new_state = state.with_phase(EmergencePhase.LOADING)
                return new_state, PhaseChanged(state.phase, EmergencePhase.LOADING)
            return state, NoChange(state, "Cannot start loading from this phase")

        case LoadingComplete():
            if state.phase == EmergencePhase.LOADING:
                new_state = state.with_phase(EmergencePhase.GALLERY)
                return new_state, PhaseChanged(state.phase, EmergencePhase.GALLERY)
            return state, NoChange(state, "Not in loading phase")

        case EnterGallery():
            if state.phase == EmergencePhase.IDLE:
                new_state = state.with_phase(EmergencePhase.GALLERY)
                return new_state, PhaseChanged(state.phase, EmergencePhase.GALLERY)
            return state, NoChange(state, "Can only enter gallery from idle")

        case EnterExplore(config=config):
            if state.phase == EmergencePhase.GALLERY:
                new_state = state.with_phase(EmergencePhase.EXPLORING).with_config(config)
                return new_state, PhaseChanged(state.phase, EmergencePhase.EXPLORING)
            return state, NoChange(state, "Can only enter explore from gallery")

        case ReturnToGallery():
            if state.phase == EmergencePhase.EXPLORING:
                new_state = state.with_phase(EmergencePhase.GALLERY)
                return new_state, PhaseChanged(state.phase, EmergencePhase.GALLERY)
            return state, NoChange(state, "Not in exploring phase")

        case StartExport():
            if state.phase == EmergencePhase.EXPLORING and state.pattern_config:
                new_state = state.with_phase(EmergencePhase.EXPORTING)
                return new_state, PhaseChanged(state.phase, EmergencePhase.EXPORTING)
            return state, NoChange(state, "Cannot export without a pattern config")

        case CancelExport():
            if state.phase == EmergencePhase.EXPORTING:
                new_state = state.with_phase(EmergencePhase.EXPLORING)
                return new_state, PhaseChanged(state.phase, EmergencePhase.EXPLORING)
            return state, NoChange(state, "Not in exporting phase")

        case CompleteExport():
            if state.phase == EmergencePhase.EXPORTING and state.pattern_config:
                new_state = state.with_phase(EmergencePhase.EXPLORING)
                export_data = {
                    "family": state.pattern_config.family.value,
                    "param1": state.pattern_config.param1,
                    "param2": state.pattern_config.param2,
                    "hue": state.pattern_config.hue,
                    "saturation": state.pattern_config.saturation,
                    "speed": state.pattern_config.speed,
                    "invert": state.pattern_config.invert,
                }
                return new_state, ExportReady(state.pattern_config, export_data)
            return state, NoChange(state, "Cannot complete export")

        case Reset():
            new_state = EmergenceState(phase=EmergencePhase.IDLE)
            return new_state, PhaseChanged(state.phase, EmergencePhase.IDLE)

        # Family/config operations
        case SelectFamily(family=family):
            if state.selected_family != family:
                new_state = state.with_family(family)
                return new_state, FamilyChanged(family, FAMILY_QUALIA[family])
            return state, NoChange(state, "Family already selected")

        case SelectPreset(preset_key=key):
            # Parse preset key (e.g., "chladni-4-5")
            try:
                parts = key.split("-")
                family = PatternFamily(parts[0])
                param1 = float(parts[1])
                param2 = float(parts[2])
                config = PatternConfig(
                    family=family,
                    param1=param1,
                    param2=param2,
                )
                new_state = state.with_config(config)
                return new_state, ConfigChanged(config)
            except (ValueError, IndexError):
                return state, NoChange(state, f"Invalid preset key: {key}")

        case ApplyConfig(config=config):
            new_state = state.with_config(config)
            return new_state, ConfigChanged(config)

        case TuneParam(param_name=name, value=value):
            if state.pattern_config is None:
                return state, NoChange(state, "No pattern config to tune")

            current = state.pattern_config
            match name:
                case "param1":
                    new_config = PatternConfig(
                        family=current.family,
                        param1=value,
                        param2=current.param2,
                        hue=current.hue,
                        saturation=current.saturation,
                        speed=current.speed,
                        invert=current.invert,
                    )
                case "param2":
                    new_config = PatternConfig(
                        family=current.family,
                        param1=current.param1,
                        param2=value,
                        hue=current.hue,
                        saturation=current.saturation,
                        speed=current.speed,
                        invert=current.invert,
                    )
                case "hue":
                    new_config = PatternConfig(
                        family=current.family,
                        param1=current.param1,
                        param2=current.param2,
                        hue=value,
                        saturation=current.saturation,
                        speed=current.speed,
                        invert=current.invert,
                    )
                case "saturation":
                    new_config = PatternConfig(
                        family=current.family,
                        param1=current.param1,
                        param2=current.param2,
                        hue=current.hue,
                        saturation=value,
                        speed=current.speed,
                        invert=current.invert,
                    )
                case "speed":
                    new_config = PatternConfig(
                        family=current.family,
                        param1=current.param1,
                        param2=current.param2,
                        hue=current.hue,
                        saturation=current.saturation,
                        speed=value,
                        invert=current.invert,
                    )
                case _:
                    return state, NoChange(state, f"Unknown param: {name}")

            new_state = state.with_config(new_config)
            return new_state, ConfigChanged(new_config)

        # Circadian
        case UpdateCircadian(phase=phase):
            if state.circadian != phase:
                new_state = state.with_circadian(phase)
                return new_state, CircadianChanged(phase, new_state.qualia)
            return state, NoChange(state, "Circadian phase unchanged")

        case _:
            return state, NoChange(state, "Unknown input type")


# =============================================================================
# Polynomial Agent
# =============================================================================


def create_emergence_polynomial(
    initial_state: EmergenceState | None = None,
) -> PolyAgent[EmergenceState, EmergenceInput, EmergenceOutput]:
    """
    Create a PolyAgent for emergence state management.

    Usage:
        poly = create_emergence_polynomial()
        state, output = poly.invoke(initial_state, SelectFamily(PatternFamily.CHLADNI))
    """
    if initial_state is None:
        initial_state = EmergenceState(phase=EmergencePhase.IDLE)

    # Create the position set (all reachable states)
    # For emergence, we enumerate phase × family × circadian combinations
    # (pattern_config and qualia are derived, so we don't enumerate them)
    positions: frozenset[EmergenceState] = frozenset(
        EmergenceState(
            phase=p,
            selected_family=f,
            circadian=c,
            qualia=(
                FAMILY_QUALIA[f].apply_modifier(CIRCADIAN_MODIFIERS[c]) if f else QualiaCoords()
            ),
        )
        for p in EmergencePhase
        for f in [None, *PatternFamily]
        for c in CircadianPhase
    )

    return PolyAgent(
        name="EMERGENCE_POLYNOMIAL",
        positions=positions,
        _directions=emergence_directions,
        _transition=emergence_transition,
    )


# Global instance for convenience
EMERGENCE_POLYNOMIAL = create_emergence_polynomial()


__all__ = [
    # Input types
    "SelectFamily",
    "SelectPreset",
    "TuneParam",
    "ApplyConfig",
    "UpdateCircadian",
    "StartLoading",
    "LoadingComplete",
    "EnterGallery",
    "EnterExplore",
    "StartExport",
    "CancelExport",
    "CompleteExport",
    "ReturnToGallery",
    "Reset",
    "EmergenceInput",
    # Output types
    "PhaseChanged",
    "FamilyChanged",
    "ConfigChanged",
    "CircadianChanged",
    "ExportReady",
    "NoChange",
    "EmergenceOutput",
    # Functions
    "emergence_directions",
    "emergence_transition",
    "create_emergence_polynomial",
    # Instance
    "EMERGENCE_POLYNOMIAL",
]
