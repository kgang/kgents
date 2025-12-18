"""
Tests for Interactive Flagship Pilots (Gallery V2).

Tests cover:
1. PolynomialPlayground - State machine visualization
2. OperadWiring - Composition diagram
3. TownLive - Streaming simulation

@see plans/gallery-pilots-top3.md
"""

from __future__ import annotations

import pytest
from agents.i.reactive.widget import RenderTarget
from protocols.projection.gallery.pilots import (
    OPERAD_DEFINITIONS,
    PILOT_REGISTRY,
    POLYNOMIAL_PRESETS,
    PilotCategory,
)

# =============================================================================
# PolynomialPlayground Tests
# =============================================================================


class TestPolynomialPlayground:
    """Test the polynomial playground pilot."""

    def test_registered_in_registry(self) -> None:
        """Polynomial playground should be registered."""
        assert "polynomial_playground" in PILOT_REGISTRY

    def test_correct_category(self) -> None:
        """Should be in INTERACTIVE category."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        assert pilot.category == PilotCategory.INTERACTIVE

    def test_has_flagship_tag(self) -> None:
        """Should have flagship tag."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        assert "flagship" in pilot.tags
        assert "teaching" in pilot.tags

    def test_renders_cli_with_traffic_light(self) -> None:
        """Should render CLI output for traffic light preset."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        result = pilot.render(RenderTarget.CLI, {"preset": "traffic_light"})
        assert result is not None
        assert "Traffic Light" in result
        assert "RED" in result
        assert "YELLOW" in result
        assert "GREEN" in result

    def test_renders_json_with_state_machine_structure(self) -> None:
        """JSON should include positions, edges, and teaching."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        result = pilot.render(RenderTarget.JSON, {"preset": "traffic_light"})
        assert result["type"] == "polynomial_playground"
        assert "positions" in result
        assert "edges" in result
        assert "teaching" in result
        assert result["interactive"] is True

    def test_renders_marimo_with_visual_elements(self) -> None:
        """Marimo/HTML should include styled state nodes."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        result = pilot.render(RenderTarget.MARIMO, {"preset": "traffic_light"})
        assert "poly-state" in result
        assert "polynomial-playground" in result

    def test_all_presets_render(self) -> None:
        """All presets should render without error."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        for preset_key in POLYNOMIAL_PRESETS.keys():
            result = pilot.render(RenderTarget.CLI, {"preset": preset_key})
            assert result is not None
            assert POLYNOMIAL_PRESETS[preset_key]["name"] in result

    def test_citizen_preset_has_right_to_rest(self) -> None:
        """Citizen preset should document Right to Rest."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        result = pilot.render(RenderTarget.JSON, {"preset": "citizen"})
        assert result.get("right_to_rest") is True
        assert "Right to Rest" in result.get("teaching", "")

    def test_valid_inputs_computed_from_edges(self) -> None:
        """Valid inputs should be computed from current state's edges."""
        pilot = PILOT_REGISTRY["polynomial_playground"]
        result = pilot.render(
            RenderTarget.JSON, {"preset": "traffic_light", "state": "RED"}
        )
        # From RED, only 'tick' leads to GREEN
        assert "valid_inputs" in result
        assert "tick" in result["valid_inputs"]


# =============================================================================
# OperadWiring Tests
# =============================================================================


class TestOperadWiring:
    """Test the operad wiring diagram pilot."""

    def test_registered_in_registry(self) -> None:
        """Operad wiring should be registered."""
        assert "operad_wiring_diagram" in PILOT_REGISTRY

    def test_correct_category(self) -> None:
        """Should be in INTERACTIVE category."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        assert pilot.category == PilotCategory.INTERACTIVE

    def test_has_flagship_tag(self) -> None:
        """Should have flagship and composition tags."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        assert "flagship" in pilot.tags
        assert "composition" in pilot.tags

    def test_renders_cli_with_operations(self) -> None:
        """CLI should show operations and their arities."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        result = pilot.render(RenderTarget.CLI, {"operad": "TOWN_OPERAD"})
        assert "TOWN_OPERAD" in result
        assert "greet" in result
        assert "gossip" in result
        assert "Operations:" in result

    def test_renders_json_with_laws(self) -> None:
        """JSON should include laws with verification status."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        result = pilot.render(RenderTarget.JSON, {"operad": "TOWN_OPERAD"})
        assert result["type"] == "operad_wiring"
        assert "laws" in result
        assert len(result["laws"]) > 0
        # All laws should be verified in demo
        for law in result["laws"]:
            assert law["verified"] is True

    def test_renders_marimo_with_palette(self) -> None:
        """Marimo/HTML should include operation palette."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        result = pilot.render(RenderTarget.MARIMO, {"operad": "TOWN_OPERAD"})
        assert "operad-wiring" in result
        assert "operad-op" in result
        assert "draggable" in result

    def test_all_operads_render(self) -> None:
        """All operads should render without error."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        for operad_key in OPERAD_DEFINITIONS.keys():
            result = pilot.render(RenderTarget.CLI, {"operad": operad_key})
            assert result is not None
            assert operad_key in result

    def test_operations_have_signatures(self) -> None:
        """Each operation should have a type signature."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        result = pilot.render(RenderTarget.JSON, {"operad": "TOWN_OPERAD"})
        for op in result["operations"]:
            assert "signature" in op
            # Type arrow can be -> or unicode arrow
            assert "->" in op["signature"] or "\u2192" in op["signature"]
            assert "arity" in op

    def test_law_equations_present(self) -> None:
        """Laws should have equations."""
        pilot = PILOT_REGISTRY["operad_wiring_diagram"]
        result = pilot.render(RenderTarget.JSON, {"operad": "TOWN_OPERAD"})
        for law in result["laws"]:
            assert "equation" in law
            assert len(law["equation"]) > 0


# =============================================================================
# TownLive Tests
# =============================================================================


class TestTownLive:
    """Test the town live streaming pilot."""

    def test_registered_in_registry(self) -> None:
        """Town live should be registered."""
        assert "town_live" in PILOT_REGISTRY

    def test_correct_category(self) -> None:
        """Should be in INTERACTIVE category."""
        pilot = PILOT_REGISTRY["town_live"]
        assert pilot.category == PilotCategory.INTERACTIVE

    def test_has_streaming_tag(self) -> None:
        """Should have streaming and sse tags."""
        pilot = PILOT_REGISTRY["town_live"]
        assert "streaming" in pilot.tags
        assert "sse" in pilot.tags
        assert "flagship" in pilot.tags

    def test_renders_cli_with_citizens(self) -> None:
        """CLI should show citizens and their phases."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.CLI)
        assert "[Town Live]" in result
        assert "Citizens:" in result
        assert "Recent Events:" in result

    def test_renders_json_with_sse_endpoint(self) -> None:
        """JSON should include SSE endpoint for streaming."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.JSON)
        assert result["type"] == "town_live"
        assert result["streaming"] is True
        assert "sse_endpoint" in result
        assert "/api/town/" in result["sse_endpoint"]

    def test_renders_marimo_with_phase_indicator(self) -> None:
        """Marimo/HTML should include phase indicator."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.MARIMO)
        assert "town-live" in result
        assert "MORNING" in result or "AFTERNOON" in result

    def test_default_citizens_present(self) -> None:
        """Default demo should have citizens."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.JSON)
        assert "citizens" in result
        assert len(result["citizens"]) > 0

    def test_citizens_have_required_fields(self) -> None:
        """Citizens should have id, name, phase, archetype."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.JSON)
        for citizen in result["citizens"]:
            assert "id" in citizen
            assert "name" in citizen
            assert "phase" in citizen
            assert "archetype" in citizen

    def test_events_have_tick_and_message(self) -> None:
        """Events should have tick number and message."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.JSON)
        assert "events" in result
        for event in result["events"]:
            assert "tick" in event
            assert "message" in event

    def test_teaching_present(self) -> None:
        """Teaching callout should be present."""
        pilot = PILOT_REGISTRY["town_live"]
        result = pilot.render(RenderTarget.JSON)
        assert "teaching" in result
        assert "polynomial" in result["teaching"].lower()


# =============================================================================
# Cross-Pilot Tests
# =============================================================================


class TestInteractivePilotsIntegration:
    """Test that all interactive pilots work together."""

    def test_all_interactive_pilots_registered(self) -> None:
        """All flagship interactive pilots should be registered."""
        expected_pilots = [
            "polynomial_playground",
            "operad_wiring_diagram",
            "town_live",
        ]
        for pilot_name in expected_pilots:
            assert pilot_name in PILOT_REGISTRY, f"{pilot_name} not registered"

    def test_all_interactive_pilots_are_interactive(self) -> None:
        """All should have interactive=True in JSON."""
        interactive_pilots = [
            "polynomial_playground",
            "operad_wiring_diagram",
            "town_live",
        ]
        for pilot_name in interactive_pilots:
            pilot = PILOT_REGISTRY[pilot_name]
            result = pilot.render(RenderTarget.JSON)
            assert result.get("interactive") is True, f"{pilot_name} not interactive"

    def test_all_interactive_pilots_have_teaching(self) -> None:
        """All should have teaching callout."""
        interactive_pilots = [
            "polynomial_playground",
            "operad_wiring_diagram",
            "town_live",
        ]
        for pilot_name in interactive_pilots:
            pilot = PILOT_REGISTRY[pilot_name]
            result = pilot.render(RenderTarget.JSON)
            assert "teaching" in result, f"{pilot_name} missing teaching"

    def test_interactive_category_count(self) -> None:
        """INTERACTIVE category should have at least 3 pilots."""
        from protocols.projection.gallery.pilots import get_pilots_by_category

        interactive_pilots = get_pilots_by_category(PilotCategory.INTERACTIVE)
        assert len(interactive_pilots) >= 3
