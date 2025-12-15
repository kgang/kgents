"""
Tests for Isometric Visualization (Micro-Experience Factory).

Phase: DEVELOP (contract tests)
Crown Jewel: plans/micro-experience-factory.md

Test Categories:
1. State serialization (IsometricState, IsometricCell, PerturbationPad)
2. Configuration (IsometricConfig, CSS transforms)
3. Widget protocol compliance (functor laws)
4. Integration with ScatterState
"""

from __future__ import annotations

from datetime import datetime

import pytest
from agents.town.isometric import (
    DEFAULT_PERTURBATION_PADS,
    IsometricCell,
    IsometricConfig,
    IsometricState,
    IsometricStyle,
    IsometricWidget,
    PerturbationPad,
    PerturbationPadState,
    scatter_point_to_cell,
    scatter_point_to_grid,
    scatter_to_isometric,
)
from agents.town.visualization import ScatterPoint, ScatterState

# =============================================================================
# IsometricConfig Tests
# =============================================================================


class TestIsometricConfig:
    """Tests for IsometricConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = IsometricConfig()

        assert config.grid_width == 20
        assert config.grid_height == 20
        assert config.cell_size == 24
        assert config.style == IsometricStyle.PIXEL
        assert config.enable_animations is True

    def test_css_transform(self) -> None:
        """CSS transform generates correct string."""
        config = IsometricConfig()
        transform = config.to_css_transform()

        assert "rotateX(60.0deg)" in transform
        assert "rotateZ(-45.0deg)" in transform

    def test_to_dict_roundtrip(self) -> None:
        """Config serializes to dict correctly."""
        config = IsometricConfig(
            grid_width=30,
            style=IsometricStyle.NEON,
        )
        data = config.to_dict()

        assert data["grid_width"] == 30
        assert data["style"] == "NEON"
        assert "css_transform" in data


# =============================================================================
# IsometricCell Tests
# =============================================================================


class TestIsometricCell:
    """Tests for IsometricCell."""

    def test_empty_cell(self) -> None:
        """Empty cells have correct defaults."""
        cell = IsometricCell(grid_x=5, grid_y=10)

        assert cell.content_type == "empty"
        assert cell.citizen_id is None
        assert cell.glyph == "·"

    def test_citizen_cell(self) -> None:
        """Citizen cells have correct content."""
        cell = IsometricCell(
            grid_x=5,
            grid_y=10,
            content_type="citizen",
            citizen_id="citizen_001",
            color="#ff0000",
            glyph="@",
        )

        assert cell.content_type == "citizen"
        assert cell.citizen_id == "citizen_001"
        assert cell.glyph == "@"

    def test_to_dict(self) -> None:
        """Cell serializes correctly."""
        cell = IsometricCell(grid_x=1, grid_y=2, is_highlighted=True)
        data = cell.to_dict()

        assert data["grid_x"] == 1
        assert data["grid_y"] == 2
        assert data["is_highlighted"] is True


# =============================================================================
# IsometricState Tests
# =============================================================================


class TestIsometricState:
    """Tests for IsometricState."""

    def test_empty_state(self) -> None:
        """Empty state has correct defaults."""
        state = IsometricState()

        assert len(state.cells) == 0
        assert len(state.citizens) == 0
        assert state.current_tick == 0
        assert state.slop_bloom_active is False

    def test_state_with_cells(self) -> None:
        """State can contain cells."""
        cells = (
            IsometricCell(grid_x=0, grid_y=0),
            IsometricCell(grid_x=1, grid_y=0, content_type="citizen"),
        )
        state = IsometricState(cells=cells)

        assert len(state.cells) == 2
        assert state.cells[1].content_type == "citizen"

    def test_to_dict_type(self) -> None:
        """State serializes with correct type."""
        state = IsometricState()
        data = state.to_dict()

        assert data["type"] == "isometric_factory"
        assert "config" in data
        assert "cells" in data
        assert "updated_at" in data

    def test_immutability(self) -> None:
        """State is immutable (frozen dataclass)."""
        state = IsometricState()

        with pytest.raises(AttributeError):
            state.current_tick = 10  # type: ignore[misc]


# =============================================================================
# PerturbationPad Tests
# =============================================================================


class TestPerturbationPad:
    """Tests for PerturbationPad."""

    def test_default_pads_exist(self) -> None:
        """Default perturbation pads are defined."""
        assert len(DEFAULT_PERTURBATION_PADS) == 4

        operations = {p.operation for p in DEFAULT_PERTURBATION_PADS}
        assert operations == {"greet", "gossip", "trade", "solo"}

    def test_pad_to_dict(self) -> None:
        """Pad serializes correctly."""
        pad = PerturbationPad(
            pad_id="test",
            operation="gossip",
            label="Test Gossip",
            hotkey="g",
        )
        data = pad.to_dict()

        assert data["operation"] == "gossip"
        assert data["hotkey"] == "g"
        assert "token_cost" in data
        assert "drama_potential" in data


class TestPerturbationPadState:
    """Tests for PerturbationPadState."""

    def test_empty_state(self) -> None:
        """Empty pad state has defaults."""
        state = PerturbationPadState()

        assert len(state.pads) == 0
        assert state.selected_pad_id is None
        assert state.global_cooldown_ms == 0

    def test_state_with_pads(self) -> None:
        """State can contain pads."""
        state = PerturbationPadState(pads=DEFAULT_PERTURBATION_PADS)

        assert len(state.pads) == 4

    def test_to_dict_type(self) -> None:
        """State serializes with correct type."""
        state = PerturbationPadState()
        data = state.to_dict()

        assert data["type"] == "perturbation_pads"


# =============================================================================
# ScatterState → IsometricState Mapping Tests (Step 3)
# =============================================================================


class TestScatterToIsometricMapping:
    """Tests for ScatterState → IsometricState mapping."""

    def test_scatter_point_to_grid_center(self) -> None:
        """Point at (0, 0) maps to center of grid."""
        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="Scholar",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            x=0.0,
            y=0.0,
        )
        config = IsometricConfig(grid_width=20, grid_height=20)

        grid_x, grid_y = scatter_point_to_grid(point, config)

        # Center of range [-1, 1] maps to center of grid [0, 19]
        assert grid_x == 9  # (0 - (-1)) / 2 * 19 = 9.5 → 9
        assert grid_y == 9

    def test_scatter_point_to_grid_corners(self) -> None:
        """Points at extremes map to grid corners."""
        config = IsometricConfig(grid_width=10, grid_height=10)

        # Top-left
        point_tl = ScatterPoint(
            citizen_id="c1",
            citizen_name="TL",
            archetype="A",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            x=-1.0,
            y=-1.0,
        )
        assert scatter_point_to_grid(point_tl, config) == (0, 0)

        # Bottom-right
        point_br = ScatterPoint(
            citizen_id="c2",
            citizen_name="BR",
            archetype="B",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            x=1.0,
            y=1.0,
        )
        assert scatter_point_to_grid(point_br, config) == (9, 9)

    def test_scatter_point_to_cell(self) -> None:
        """Point converts to cell with correct properties."""
        point = ScatterPoint(
            citizen_id="citizen_001",
            citizen_name="Alice",
            archetype="Scholar",
            warmth=0.8,
            curiosity=0.9,
            trust=0.7,
            creativity=0.6,
            patience=0.5,
            resilience=0.4,
            ambition=0.3,
            x=0.5,
            y=-0.5,
            color="#ff0000",
            is_selected=True,
            is_evolving=True,
        )
        config = IsometricConfig(grid_width=20, grid_height=20)

        cell = scatter_point_to_cell(point, config)

        assert cell.content_type == "citizen"
        assert cell.citizen_id == "citizen_001"
        assert cell.color == "#ff0000"
        assert cell.glyph == "S"  # First letter of "Scholar"
        assert cell.is_selected is True
        assert cell.is_highlighted is True  # From is_evolving

    def test_scatter_to_isometric_empty(self) -> None:
        """Empty scatter state produces empty isometric state."""
        scatter = ScatterState()
        isometric = scatter_to_isometric(scatter)

        assert len(isometric.cells) == 0
        assert len(isometric.citizens) == 0
        assert isometric.selected_cell is None

    def test_scatter_to_isometric_with_points(self) -> None:
        """Scatter state with points produces isometric cells."""
        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="Alice",
                archetype="Scholar",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=-0.5,
                y=0.0,
            ),
            ScatterPoint(
                citizen_id="c2",
                citizen_name="Bob",
                archetype="Trader",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=0.5,
                y=0.0,
            ),
        )
        scatter = ScatterState(points=points)
        isometric = scatter_to_isometric(scatter)

        assert len(isometric.cells) == 2
        assert isometric.cells[0].citizen_id == "c1"
        assert isometric.cells[1].citizen_id == "c2"
        # Different x positions should yield different grid_x
        assert isometric.cells[0].grid_x != isometric.cells[1].grid_x

    def test_scatter_to_isometric_selection_preserved(self) -> None:
        """Selection state is preserved in mapping."""
        points = (
            ScatterPoint(
                citizen_id="selected_citizen",
                citizen_name="Selected",
                archetype="A",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=0.0,
                y=0.0,
            ),
        )
        scatter = ScatterState(
            points=points,
            selected_citizen_id="selected_citizen",
        )
        isometric = scatter_to_isometric(scatter)

        assert isometric.selected_cell is not None
        assert isometric.selected_cell == (
            isometric.cells[0].grid_x,
            isometric.cells[0].grid_y,
        )

    def test_scatter_to_isometric_auto_range(self) -> None:
        """Auto-computed range adapts to point positions."""
        # Create points outside default [-1, 1] range
        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="A",
                archetype="A",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=0.0,
                y=0.0,
            ),
            ScatterPoint(
                citizen_id="c2",
                citizen_name="B",
                archetype="B",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=100.0,
                y=100.0,
            ),
        )
        scatter = ScatterState(points=points)
        config = IsometricConfig(grid_width=10, grid_height=10)
        isometric = scatter_to_isometric(scatter, config)

        # Both points should map to valid grid cells
        assert 0 <= isometric.cells[0].grid_x < 10
        assert 0 <= isometric.cells[1].grid_x < 10
        # Points are spread across the grid
        assert isometric.cells[0].grid_x < isometric.cells[1].grid_x


# =============================================================================
# Integration Contract Tests (Stubs - Future phases)
# =============================================================================


class TestIsometricWidgetContract:
    """Contract tests for IsometricWidget protocol."""

    def test_functor_law_identity(self) -> None:
        """isometric.map(id) ≡ isometric"""
        # Create widget with some state
        cells = (
            IsometricCell(
                grid_x=5, grid_y=5, content_type="citizen", citizen_id="c1", glyph="T"
            ),
        )
        state = IsometricState(cells=cells, current_tick=10)
        widget = IsometricWidget(state)

        # Apply identity function
        def identity(s: IsometricState) -> IsometricState:
            return s

        mapped = widget.map(identity)

        # Verify state is preserved
        assert mapped.state.value.current_tick == widget.state.value.current_tick
        assert len(mapped.state.value.cells) == len(widget.state.value.cells)
        assert (
            mapped.state.value.cells[0].citizen_id
            == widget.state.value.cells[0].citizen_id
        )

    def test_functor_law_composition(self) -> None:
        """isometric.map(f).map(g) ≡ isometric.map(f . g)"""
        state = IsometricState(current_tick=1, entropy_level=0.1)
        widget = IsometricWidget(state)

        # Define two functions
        def f(s: IsometricState) -> IsometricState:
            return IsometricState(
                config=s.config,
                cells=s.cells,
                current_tick=s.current_tick + 1,
                entropy_level=s.entropy_level,
            )

        def g(s: IsometricState) -> IsometricState:
            return IsometricState(
                config=s.config,
                cells=s.cells,
                current_tick=s.current_tick * 2,
                entropy_level=s.entropy_level,
            )

        # f . g composition
        def fg(s: IsometricState) -> IsometricState:
            return g(f(s))

        # Apply in two steps
        result_two_steps = widget.map(f).map(g)

        # Apply composed function
        result_composed = widget.map(fg)

        # Verify equivalence
        assert (
            result_two_steps.state.value.current_tick
            == result_composed.state.value.current_tick
        )
        # (1 + 1) * 2 = 4
        assert result_two_steps.state.value.current_tick == 4

    def test_project_cli(self) -> None:
        """CLI projection returns ASCII grid."""
        # Create widget with some cells
        cells = (
            IsometricCell(
                grid_x=5, grid_y=5, content_type="citizen", citizen_id="c1", glyph="S"
            ),
            IsometricCell(
                grid_x=10, grid_y=10, content_type="citizen", citizen_id="c2", glyph="T"
            ),
        )
        state = IsometricState(
            cells=cells,
            config=IsometricConfig(grid_width=20, grid_height=20),
            current_tick=5,
            entropy_level=0.25,
        )
        widget = IsometricWidget(state)

        cli_output = widget.to_cli()

        # Verify output contains expected elements
        assert "ISOMETRIC FACTORY" in cli_output
        assert "Day" in cli_output
        assert "Entropy:" in cli_output
        assert "0.25" in cli_output
        assert "Citizens: 2" in cli_output
        # Glyphs should appear
        assert "S" in cli_output
        assert "T" in cli_output
        # New elements from enhanced rendering
        assert "[G]reet" in cli_output  # Perturbation pads
        assert "═" in cli_output  # Border characters

    def test_project_json(self) -> None:
        """JSON projection returns IsometricState.to_dict()."""
        cells = (
            IsometricCell(grid_x=1, grid_y=2, content_type="citizen", citizen_id="c1"),
        )
        state = IsometricState(cells=cells, current_tick=3)
        widget = IsometricWidget(state)

        json_output = widget.to_json()

        assert json_output["type"] == "isometric_factory"
        assert json_output["current_tick"] == 3
        assert len(json_output["cells"]) == 1
        assert json_output["cells"][0]["citizen_id"] == "c1"

    def test_update_from_scatter(self) -> None:
        """Widget updates from ScatterState (via scatter_to_isometric)."""
        # This test validates Step 3 implementation
        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="Test",
                archetype="Tester",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=0.0,
                y=0.0,
            ),
        )
        scatter = ScatterState(points=points)
        isometric = scatter_to_isometric(scatter)

        assert len(isometric.cells) == 1
        assert isometric.cells[0].glyph == "T"  # First letter of "Tester"

    def test_update_from_scatter_widget(self) -> None:
        """Widget.update_from_scatter updates cells correctly."""
        widget = IsometricWidget()
        points = (
            ScatterPoint(
                citizen_id="citizen_alice",
                citizen_name="Alice",
                archetype="Scholar",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                x=0.0,
                y=0.0,
            ),
        )
        scatter = ScatterState(points=points)

        widget.update_from_scatter(scatter)

        assert len(widget.state.value.cells) == 1
        assert widget.state.value.cells[0].citizen_id == "citizen_alice"
        assert widget.state.value.cells[0].glyph == "S"  # First letter of "Scholar"

    def test_select_cell(self) -> None:
        """select_cell updates selected_cell state."""
        widget = IsometricWidget()
        assert widget.state.value.selected_cell is None

        widget.select_cell(5, 10)

        assert widget.state.value.selected_cell == (5, 10)

    def test_hover_cell(self) -> None:
        """hover_cell updates hovered_cell state."""
        widget = IsometricWidget()
        assert widget.state.value.hovered_cell is None

        widget.hover_cell(3, 7)

        assert widget.state.value.hovered_cell == (3, 7)

    def test_set_tick(self) -> None:
        """set_tick updates current_tick state."""
        widget = IsometricWidget()
        assert widget.state.value.current_tick == 0

        widget.set_tick(42)

        assert widget.state.value.current_tick == 42

    def test_toggle_slop_bloom(self) -> None:
        """toggle_slop_bloom toggles slop_bloom_active state."""
        widget = IsometricWidget()
        assert widget.state.value.slop_bloom_active is False

        widget.toggle_slop_bloom()
        assert widget.state.value.slop_bloom_active is True

        widget.toggle_slop_bloom()
        assert widget.state.value.slop_bloom_active is False

    def test_with_state_creates_new_widget(self) -> None:
        """with_state returns new widget with transformed state."""
        original = IsometricWidget(IsometricState(current_tick=1))
        new_state = IsometricState(current_tick=100)

        transformed = original.with_state(new_state)

        # Original unchanged
        assert original.state.value.current_tick == 1
        # New widget has new state
        assert transformed.state.value.current_tick == 100

    def test_update_from_event(self) -> None:
        """Widget updates from TownEvent."""
        from agents.town.flux import TownEvent, TownPhase

        widget = IsometricWidget(IsometricState(current_tick=5, entropy_level=0.1))

        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="gossip",
            participants=["Alice", "Bob"],
            success=True,
            message="Alice gossiped with Bob",
            drama_contribution=0.3,
            metadata={"pipeline_id": "pipe_001"},
        )

        widget.update_from_event(event)

        # Tick should advance
        assert widget.state.value.current_tick == 6
        # Entropy should increase
        assert widget.state.value.entropy_level > 0.1
        # Pipeline should be tracked
        assert "pipe_001" in widget.state.value.active_pipelines

    def test_update_from_event_without_pipeline(self) -> None:
        """Widget updates from TownEvent without pipeline_id."""
        from agents.town.flux import TownEvent, TownPhase

        widget = IsometricWidget()

        event = TownEvent(
            phase=TownPhase.AFTERNOON,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            drama_contribution=0.1,
        )

        initial_tick = widget.state.value.current_tick
        widget.update_from_event(event)

        # Tick should still advance
        assert widget.state.value.current_tick == initial_tick + 1
        # No pipelines added
        assert len(widget.state.value.active_pipelines) == 0
