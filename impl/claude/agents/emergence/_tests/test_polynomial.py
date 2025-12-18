"""
Tests for EMERGENCE_POLYNOMIAL state machine.

Verifies:
1. Phase transitions (IDLE → LOADING → GALLERY → EXPLORING → EXPORTING)
2. Family selection and config updates
3. Circadian modulation
4. Qualia coherence
5. Invalid transition rejection

Target: 20+ tests for polynomial alone.
"""

from datetime import datetime

import pytest

from agents.emergence import (
    # Polynomial
    EMERGENCE_POLYNOMIAL,
    ApplyConfig,
    CancelExport,
    CircadianChanged,
    CircadianPhase,
    CompleteExport,
    ConfigChanged,
    # State
    EmergencePhase,
    EmergenceState,
    EnterExplore,
    EnterGallery,
    ExportReady,
    FamilyChanged,
    LoadingComplete,
    NoChange,
    PatternConfig,
    PatternFamily,
    # Outputs
    PhaseChanged,
    QualiaCoords,
    Reset,
    ReturnToGallery,
    # Inputs
    SelectFamily,
    SelectPreset,
    StartExport,
    StartLoading,
    TuneParam,
    UpdateCircadian,
    create_emergence_polynomial,
    emergence_directions,
    emergence_transition,
)

# =============================================================================
# Initial State Tests
# =============================================================================


class TestInitialState:
    """Test initial polynomial state."""

    def test_default_initial_phase_is_idle(self):
        """Default state starts in IDLE phase."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        assert state.phase == EmergencePhase.IDLE

    def test_default_initial_has_no_family(self):
        """Default state has no selected family."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        assert state.selected_family is None

    def test_default_initial_has_noon_circadian(self):
        """Default circadian is NOON."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        assert state.circadian == CircadianPhase.NOON

    def test_polynomial_factory(self):
        """Factory creates valid polynomial."""
        poly = create_emergence_polynomial()
        assert poly.name == "EMERGENCE_POLYNOMIAL"

    def test_global_instance_exists(self):
        """Global EMERGENCE_POLYNOMIAL exists."""
        assert EMERGENCE_POLYNOMIAL is not None
        assert EMERGENCE_POLYNOMIAL.name == "EMERGENCE_POLYNOMIAL"


# =============================================================================
# Phase Transition Tests
# =============================================================================


class TestPhaseTransitions:
    """Test phase machine transitions."""

    def test_idle_to_gallery(self):
        """Can transition from IDLE to GALLERY."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        new_state, output = emergence_transition(state, EnterGallery())

        assert new_state.phase == EmergencePhase.GALLERY
        assert isinstance(output, PhaseChanged)
        assert output.old_phase == EmergencePhase.IDLE
        assert output.new_phase == EmergencePhase.GALLERY

    def test_idle_to_loading(self):
        """Can transition from IDLE to LOADING."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        new_state, output = emergence_transition(state, StartLoading())

        assert new_state.phase == EmergencePhase.LOADING
        assert isinstance(output, PhaseChanged)

    def test_loading_to_gallery(self):
        """Can transition from LOADING to GALLERY."""
        state = EmergenceState(phase=EmergencePhase.LOADING)
        new_state, output = emergence_transition(state, LoadingComplete())

        assert new_state.phase == EmergencePhase.GALLERY
        assert isinstance(output, PhaseChanged)

    def test_gallery_to_exploring(self):
        """Can transition from GALLERY to EXPLORING."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, EnterExplore(config=config))

        assert new_state.phase == EmergencePhase.EXPLORING
        assert new_state.pattern_config == config
        assert isinstance(output, PhaseChanged)

    def test_exploring_to_gallery(self):
        """Can return from EXPLORING to GALLERY."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(
            phase=EmergencePhase.EXPLORING,
            pattern_config=config,
        )
        new_state, output = emergence_transition(state, ReturnToGallery())

        assert new_state.phase == EmergencePhase.GALLERY
        assert isinstance(output, PhaseChanged)

    def test_exploring_to_exporting(self):
        """Can transition from EXPLORING to EXPORTING."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(
            phase=EmergencePhase.EXPLORING,
            pattern_config=config,
        )
        new_state, output = emergence_transition(state, StartExport())

        assert new_state.phase == EmergencePhase.EXPORTING
        assert isinstance(output, PhaseChanged)

    def test_exporting_cancel(self):
        """Can cancel export and return to EXPLORING."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(
            phase=EmergencePhase.EXPORTING,
            pattern_config=config,
        )
        new_state, output = emergence_transition(state, CancelExport())

        assert new_state.phase == EmergencePhase.EXPLORING
        assert isinstance(output, PhaseChanged)

    def test_exporting_complete(self):
        """Completing export returns ExportReady."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(
            phase=EmergencePhase.EXPORTING,
            pattern_config=config,
        )
        new_state, output = emergence_transition(state, CompleteExport())

        assert new_state.phase == EmergencePhase.EXPLORING
        assert isinstance(output, ExportReady)
        assert output.config == config
        assert output.export_data["family"] == "chladni"

    def test_reset_returns_to_idle(self):
        """Reset from any phase returns to IDLE."""
        state = EmergenceState(
            phase=EmergencePhase.EXPLORING,
            selected_family=PatternFamily.MANDALA,
        )
        new_state, output = emergence_transition(state, Reset())

        assert new_state.phase == EmergencePhase.IDLE
        assert isinstance(output, PhaseChanged)


# =============================================================================
# Invalid Transition Tests
# =============================================================================


class TestInvalidTransitions:
    """Test that invalid transitions are rejected."""

    def test_cannot_enter_explore_from_idle(self):
        """Cannot EnterExplore from IDLE (must go through GALLERY)."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
        )
        state = EmergenceState(phase=EmergencePhase.IDLE)
        new_state, output = emergence_transition(state, EnterExplore(config=config))

        assert new_state.phase == EmergencePhase.IDLE  # Unchanged
        assert isinstance(output, NoChange)

    def test_cannot_export_without_config(self):
        """Cannot StartExport without a pattern config."""
        state = EmergenceState(
            phase=EmergencePhase.EXPLORING,
            pattern_config=None,
        )
        new_state, output = emergence_transition(state, StartExport())

        assert new_state.phase == EmergencePhase.EXPLORING  # Unchanged
        assert isinstance(output, NoChange)

    def test_cannot_return_to_gallery_from_idle(self):
        """Cannot ReturnToGallery from IDLE."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        new_state, output = emergence_transition(state, ReturnToGallery())

        assert new_state.phase == EmergencePhase.IDLE  # Unchanged
        assert isinstance(output, NoChange)


# =============================================================================
# Family Selection Tests
# =============================================================================


class TestFamilySelection:
    """Test family selection and config updates."""

    def test_select_family_updates_state(self):
        """SelectFamily changes selected_family."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, SelectFamily(PatternFamily.MANDALA))

        assert new_state.selected_family == PatternFamily.MANDALA
        assert isinstance(output, FamilyChanged)
        assert output.family == PatternFamily.MANDALA

    def test_select_family_updates_qualia(self):
        """SelectFamily also updates qualia to family's base coordinates."""
        from agents.emergence.types import FAMILY_QUALIA

        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, _ = emergence_transition(state, SelectFamily(PatternFamily.FLOW))

        expected_qualia = FAMILY_QUALIA[PatternFamily.FLOW]
        assert new_state.qualia.warmth == expected_qualia.warmth

    def test_select_same_family_no_change(self):
        """Selecting already-selected family returns NoChange."""
        state = EmergenceState(
            phase=EmergencePhase.GALLERY,
            selected_family=PatternFamily.CHLADNI,
        )
        new_state, output = emergence_transition(state, SelectFamily(PatternFamily.CHLADNI))

        assert isinstance(output, NoChange)

    def test_apply_config(self):
        """ApplyConfig updates the pattern configuration."""
        config = PatternConfig(
            family=PatternFamily.SPIRAL,
            param1=3.0,
            param2=7.0,
            hue=0.8,
        )
        state = EmergenceState(phase=EmergencePhase.EXPLORING)
        new_state, output = emergence_transition(state, ApplyConfig(config=config))

        assert new_state.pattern_config == config
        assert new_state.selected_family == PatternFamily.SPIRAL
        assert isinstance(output, ConfigChanged)


# =============================================================================
# Parameter Tuning Tests
# =============================================================================


class TestParameterTuning:
    """Test parameter tuning in EXPLORING phase."""

    @pytest.fixture
    def exploring_state(self):
        """State in EXPLORING with a config."""
        config = PatternConfig(
            family=PatternFamily.CHLADNI,
            param1=4.0,
            param2=5.0,
            hue=0.55,
            saturation=0.7,
            speed=0.5,
        )
        return EmergenceState(
            phase=EmergencePhase.EXPLORING,
            selected_family=PatternFamily.CHLADNI,
            pattern_config=config,
        )

    def test_tune_param1(self, exploring_state):
        """Can tune param1."""
        new_state, output = emergence_transition(exploring_state, TuneParam("param1", 6.0))

        assert new_state.pattern_config.param1 == 6.0
        assert isinstance(output, ConfigChanged)

    def test_tune_param2(self, exploring_state):
        """Can tune param2."""
        new_state, output = emergence_transition(exploring_state, TuneParam("param2", 8.0))

        assert new_state.pattern_config.param2 == 8.0
        assert isinstance(output, ConfigChanged)

    def test_tune_hue(self, exploring_state):
        """Can tune hue."""
        new_state, output = emergence_transition(exploring_state, TuneParam("hue", 0.3))

        assert new_state.pattern_config.hue == 0.3
        assert isinstance(output, ConfigChanged)

    def test_tune_saturation(self, exploring_state):
        """Can tune saturation."""
        new_state, output = emergence_transition(exploring_state, TuneParam("saturation", 0.9))

        assert new_state.pattern_config.saturation == 0.9
        assert isinstance(output, ConfigChanged)

    def test_tune_speed(self, exploring_state):
        """Can tune speed."""
        new_state, output = emergence_transition(exploring_state, TuneParam("speed", 1.0))

        assert new_state.pattern_config.speed == 1.0
        assert isinstance(output, ConfigChanged)

    def test_tune_unknown_param_no_change(self, exploring_state):
        """Tuning unknown param returns NoChange."""
        new_state, output = emergence_transition(exploring_state, TuneParam("unknown", 5.0))

        assert isinstance(output, NoChange)

    def test_tune_without_config_no_change(self):
        """Tuning without config returns NoChange."""
        state = EmergenceState(phase=EmergencePhase.EXPLORING)
        new_state, output = emergence_transition(state, TuneParam("param1", 5.0))

        assert isinstance(output, NoChange)


# =============================================================================
# Preset Selection Tests
# =============================================================================


class TestPresetSelection:
    """Test preset key parsing and application."""

    def test_valid_preset_key(self):
        """Valid preset key is parsed and applied."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, SelectPreset("chladni-4-5.0"))

        assert new_state.pattern_config.family == PatternFamily.CHLADNI
        assert new_state.pattern_config.param1 == 4.0
        assert new_state.pattern_config.param2 == 5.0
        assert isinstance(output, ConfigChanged)

    def test_invalid_preset_key_no_change(self):
        """Invalid preset key returns NoChange."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, SelectPreset("invalid"))

        assert isinstance(output, NoChange)

    def test_invalid_family_no_change(self):
        """Unknown family in preset key returns NoChange."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, SelectPreset("unknown-4-5"))

        assert isinstance(output, NoChange)


# =============================================================================
# Circadian Tests
# =============================================================================


class TestCircadianModulation:
    """Test circadian phase updates."""

    def test_update_circadian_to_dawn(self):
        """Can update circadian to DAWN."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, UpdateCircadian(CircadianPhase.DAWN))

        assert new_state.circadian == CircadianPhase.DAWN
        assert isinstance(output, CircadianChanged)
        assert output.phase == CircadianPhase.DAWN

    def test_update_circadian_to_dusk(self):
        """Can update circadian to DUSK."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        new_state, output = emergence_transition(state, UpdateCircadian(CircadianPhase.DUSK))

        assert new_state.circadian == CircadianPhase.DUSK
        assert isinstance(output, CircadianChanged)

    def test_update_circadian_modifies_qualia(self):
        """Circadian change modifies qualia."""
        state = EmergenceState(
            phase=EmergencePhase.GALLERY,
            selected_family=PatternFamily.CHLADNI,
        )
        new_state, output = emergence_transition(state, UpdateCircadian(CircadianPhase.DUSK))

        # DUSK has warmth +0.4, so qualia.warmth should increase
        assert isinstance(output, CircadianChanged)
        assert output.qualia.warmth > state.qualia.warmth

    def test_same_circadian_no_change(self):
        """Updating to same circadian returns NoChange."""
        state = EmergenceState(
            phase=EmergencePhase.GALLERY,
            circadian=CircadianPhase.NOON,
        )
        new_state, output = emergence_transition(state, UpdateCircadian(CircadianPhase.NOON))

        assert isinstance(output, NoChange)


# =============================================================================
# Directions Tests
# =============================================================================


class TestDirections:
    """Test available directions from each phase."""

    def test_idle_directions(self):
        """IDLE allows StartLoading, EnterGallery, SelectFamily."""
        state = EmergenceState(phase=EmergencePhase.IDLE)
        dirs = emergence_directions(state)

        assert StartLoading in dirs
        assert EnterGallery in dirs
        assert SelectFamily in dirs
        assert UpdateCircadian in dirs
        assert Reset in dirs

    def test_loading_directions(self):
        """LOADING only allows LoadingComplete."""
        state = EmergenceState(phase=EmergencePhase.LOADING)
        dirs = emergence_directions(state)

        assert LoadingComplete in dirs
        assert UpdateCircadian in dirs
        assert Reset in dirs
        assert EnterGallery not in dirs

    def test_gallery_directions(self):
        """GALLERY allows selection and exploration."""
        state = EmergenceState(phase=EmergencePhase.GALLERY)
        dirs = emergence_directions(state)

        assert SelectFamily in dirs
        assert SelectPreset in dirs
        assert EnterExplore in dirs
        assert TuneParam in dirs
        assert StartExport not in dirs

    def test_exploring_directions(self):
        """EXPLORING allows tuning, export, and return."""
        state = EmergenceState(phase=EmergencePhase.EXPLORING)
        dirs = emergence_directions(state)

        assert TuneParam in dirs
        assert ApplyConfig in dirs
        assert StartExport in dirs
        assert ReturnToGallery in dirs

    def test_exporting_directions(self):
        """EXPORTING only allows cancel or complete."""
        state = EmergenceState(phase=EmergencePhase.EXPORTING)
        dirs = emergence_directions(state)

        assert CancelExport in dirs
        assert CompleteExport in dirs
        assert TuneParam not in dirs
