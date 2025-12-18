"""
Tests for Gallery Polynomial and Operad.

Validates:
- GalleryPolynomial state transitions
- GALLERY_OPERAD law verification
- Visualization data generation
"""

import pytest
from agents.gallery import (
    GALLERY_OPERAD,
    GALLERY_POLYNOMIAL,
    GalleryPhase,
    gallery_visualization,
)
from agents.gallery.operad import gallery_operad_visualization
from agents.gallery.polynomial import (
    GALLERY_INITIAL,
    CloseInput,
    FilterInput,
    GalleryState,
    OverrideInput,
    SelectPilotInput,
    SimulateInput,
    StepInput,
    VerifyInput,
)
from agents.operad.core import LawStatus, OperadRegistry


class TestGalleryPolynomial:
    """Test GalleryPolynomial state machine."""

    def test_polynomial_exists(self):
        """Polynomial is properly constructed."""
        assert GALLERY_POLYNOMIAL is not None
        assert GALLERY_POLYNOMIAL.name == "GalleryPolynomial"
        assert len(GALLERY_POLYNOMIAL.positions) == 4

    def test_initial_state_is_browsing(self):
        """Initial state is BROWSING."""
        assert GALLERY_INITIAL.phase == GalleryPhase.BROWSING
        assert GALLERY_INITIAL.active_category == "ALL"
        assert GALLERY_INITIAL.selected_pilot is None

    def test_browsing_to_inspecting(self):
        """Selecting a pilot transitions to INSPECTING."""
        state = GALLERY_INITIAL
        input = SelectPilotInput(pilot_name="glyph_idle")
        new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.phase == GalleryPhase.INSPECTING
        assert new_state.selected_pilot == "glyph_idle"
        assert "Inspecting" in output.message

    def test_inspecting_to_simulating(self):
        """Starting simulation transitions to SIMULATING."""
        state = GalleryState(
            phase=GalleryPhase.INSPECTING,
            selected_pilot="citizen_polynomial",
        )
        input = SimulateInput()
        new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.phase == GalleryPhase.SIMULATING
        assert new_state.simulation_state == "initial"
        assert "Started simulation" in output.message

    def test_inspecting_to_verifying(self):
        """Verifying laws transitions to VERIFYING."""
        state = GalleryState(
            phase=GalleryPhase.INSPECTING,
            selected_pilot="town_operad",
        )
        input = VerifyInput()
        new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.phase == GalleryPhase.VERIFYING
        assert "Verifying laws" in output.message

    def test_simulating_step(self):
        """Stepping advances simulation state."""
        state = GalleryState(
            phase=GalleryPhase.SIMULATING,
            selected_pilot="citizen_polynomial",
            simulation_state="initial",
        )
        input = StepInput(input_value="work")
        new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.phase == GalleryPhase.SIMULATING
        assert new_state.simulation_state == "stepped_work"
        assert "Stepped with" in output.message

    def test_close_returns_to_browsing(self):
        """Close input returns to BROWSING from any state."""
        for phase in [
            GalleryPhase.INSPECTING,
            GalleryPhase.SIMULATING,
            GalleryPhase.VERIFYING,
        ]:
            state = GalleryState(phase=phase)
            input = CloseInput()
            new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

            assert new_state.phase == GalleryPhase.BROWSING
            assert "Returned to browsing" in output.message

    def test_filter_preserves_browsing(self):
        """Filtering stays in BROWSING phase."""
        state = GALLERY_INITIAL
        input = FilterInput(category="CARDS")
        new_state, output = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.phase == GalleryPhase.BROWSING
        assert new_state.active_category == "CARDS"

    def test_overrides_preserved_across_transitions(self):
        """Overrides are preserved when navigating."""
        state = GalleryState(
            phase=GalleryPhase.BROWSING,
            overrides=OverrideInput(entropy=0.5, seed=42),
        )
        input = SelectPilotInput(pilot_name="test_pilot")
        new_state, _ = GALLERY_POLYNOMIAL.transition(state, input)

        assert new_state.overrides is not None
        assert new_state.overrides.entropy == 0.5
        assert new_state.overrides.seed == 42


class TestGalleryOperad:
    """Test GALLERY_OPERAD operations and laws."""

    def test_operad_exists(self):
        """Operad is properly constructed."""
        assert GALLERY_OPERAD is not None
        assert GALLERY_OPERAD.name == "GalleryOperad"

    def test_operad_has_expected_operations(self):
        """All expected operations are registered."""
        expected = {"reset", "filter", "select", "override", "compare", "compose"}
        actual = set(GALLERY_OPERAD.operations.keys())
        assert expected == actual

    def test_operad_has_laws(self):
        """Operad has laws defined."""
        assert len(GALLERY_OPERAD.laws) >= 3
        law_names = {law.name for law in GALLERY_OPERAD.laws}
        assert "filter_identity" in law_names
        assert "override_deterministic" in law_names
        assert "compare_symmetric" in law_names

    def test_operad_registered_globally(self):
        """Operad is registered in OperadRegistry."""
        found = OperadRegistry.get("GalleryOperad")
        assert found is not None
        assert found.name == "GalleryOperad"

    def test_law_verification(self):
        """Laws can be verified."""
        results = GALLERY_OPERAD.verify_all_laws()
        assert len(results) >= 3

        for result in results:
            assert result.passed, f"Law {result.law_name} failed: {result.message}"

    def test_operation_arities(self):
        """Operations have correct arities."""
        assert GALLERY_OPERAD.operations["reset"].arity == 0
        assert GALLERY_OPERAD.operations["filter"].arity == 1
        assert GALLERY_OPERAD.operations["select"].arity == 1
        assert GALLERY_OPERAD.operations["override"].arity == 1
        assert GALLERY_OPERAD.operations["compare"].arity == 2
        assert GALLERY_OPERAD.operations["compose"].arity == 2


class TestGalleryVisualization:
    """Test visualization data generation."""

    def test_polynomial_visualization(self):
        """Polynomial visualization data is complete."""
        viz = gallery_visualization()

        assert viz["id"] == "gallery"
        assert viz["name"] == "GalleryPolynomial"
        assert len(viz["positions"]) == 4
        assert len(viz["edges"]) >= 7

        # Check position structure
        position_ids = {p["id"] for p in viz["positions"]}
        assert position_ids == {"BROWSING", "INSPECTING", "SIMULATING", "VERIFYING"}

        # Check all positions have required fields
        for pos in viz["positions"]:
            assert "id" in pos
            assert "label" in pos
            assert "icon" in pos
            assert "is_current" in pos
            assert "is_terminal" in pos
            assert "color" in pos

    def test_operad_visualization(self):
        """Operad visualization data is complete."""
        viz = gallery_operad_visualization()

        assert viz["name"] == "GalleryOperad"
        assert len(viz["operations"]) == 6
        assert len(viz["laws"]) >= 3

        # Check operation structure
        for op in viz["operations"]:
            assert "name" in op
            assert "arity" in op
            assert "signature" in op
            assert "description" in op

        # Check law structure
        for law in viz["laws"]:
            assert "name" in law
            assert "equation" in law
            assert "description" in law


class TestGalleryIntegration:
    """Integration tests for gallery as vertical slice."""

    def test_polynomial_and_operad_coexist(self):
        """Both polynomial and operad can be used together."""
        # Polynomial handles navigation state
        state = GALLERY_INITIAL
        state, _ = GALLERY_POLYNOMIAL.transition(
            state, SelectPilotInput(pilot_name="test")
        )

        # Operad handles composition
        reset_op = GALLERY_OPERAD.get("reset")
        assert reset_op is not None
        reset_agent = reset_op.compose()
        assert reset_agent.name == "reset"

    def test_visualization_data_consistent(self):
        """Visualization data matches actual structures."""
        poly_viz = gallery_visualization()
        operad_viz = gallery_operad_visualization()

        # Polynomial phases match visualization positions
        poly_phases = {p.name for p in GalleryPhase}
        viz_positions = {p["id"] for p in poly_viz["positions"]}
        assert poly_phases == viz_positions

        # Operad operations match visualization
        operad_ops = set(GALLERY_OPERAD.operations.keys())
        viz_ops = {op["name"] for op in operad_viz["operations"]}
        assert operad_ops == viz_ops
