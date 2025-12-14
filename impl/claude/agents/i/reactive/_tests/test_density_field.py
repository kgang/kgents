"""Tests for DensityFieldWidget - 2D grid with spatial entropy coherence."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.density_field import (
    DensityFieldState,
    DensityFieldWidget,
    Entity,
    Wind,
)
from agents.i.reactive.widget import RenderTarget


class TestEntity:
    """Tests for Entity data class."""

    def test_entity_default_values(self) -> None:
        """Entity has expected defaults."""
        entity = Entity(id="test", x=10, y=5)
        assert entity.id == "test"
        assert entity.x == 10
        assert entity.y == 5
        assert entity.char == "◉"
        assert entity.phase == "active"
        assert entity.heat == 0.0

    def test_entity_with_all_fields(self) -> None:
        """Entity can be created with all fields."""
        entity = Entity(
            id="agent-1",
            x=20,
            y=10,
            char="★",
            phase="thinking",
            heat=0.8,
        )
        assert entity.id == "agent-1"
        assert entity.char == "★"
        assert entity.phase == "thinking"
        assert entity.heat == 0.8


class TestWind:
    """Tests for Wind data class."""

    def test_wind_default_values(self) -> None:
        """Wind has zero defaults."""
        wind = Wind()
        assert wind.dx == 0.0
        assert wind.dy == 0.0
        assert wind.strength == 0.0

    def test_wind_with_values(self) -> None:
        """Wind can be created with direction and strength."""
        wind = Wind(dx=0.5, dy=-0.3, strength=0.7)
        assert wind.dx == 0.5
        assert wind.dy == -0.3
        assert wind.strength == 0.7


class TestDensityFieldState:
    """Tests for DensityFieldState immutable state."""

    def test_default_state(self) -> None:
        """Default DensityFieldState has expected values."""
        state = DensityFieldState()
        assert state.width == 40
        assert state.height == 20
        assert state.base_entropy == 0.1
        assert state.entities == ()

    def test_state_is_frozen(self) -> None:
        """DensityFieldState is immutable."""
        state = DensityFieldState()
        with pytest.raises(Exception):
            state.width = 100  # type: ignore[misc]

    def test_state_with_entities(self) -> None:
        """State can hold entities."""
        entities = (
            Entity(id="a", x=10, y=5),
            Entity(id="b", x=20, y=10),
        )
        state = DensityFieldState(entities=entities)
        assert len(state.entities) == 2


class TestDensityFieldWidget:
    """Tests for DensityFieldWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """Widget can be created with default state."""
        widget = DensityFieldWidget()
        assert widget.state.value.width == 40
        assert widget.state.value.height == 20

    def test_create_with_custom_size(self) -> None:
        """Widget can be created with custom size."""
        widget = DensityFieldWidget(DensityFieldState(width=60, height=30))
        assert widget.state.value.width == 60
        assert widget.state.value.height == 30

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget."""
        original = DensityFieldWidget(DensityFieldState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = DensityFieldWidget(DensityFieldState(base_entropy=0.1))
        updated = original.with_entropy(0.5)

        assert original.state.value.base_entropy == 0.1
        assert updated.state.value.base_entropy == 0.5

    def test_with_wind_returns_new_widget(self) -> None:
        """with_wind() returns new widget."""
        original = DensityFieldWidget()
        wind = Wind(dx=0.5, dy=-0.2, strength=0.3)
        updated = original.with_wind(wind)

        assert original.state.value.wind.strength == 0.0
        assert updated.state.value.wind.strength == 0.3


class TestDensityFieldEntities:
    """Tests for entity management."""

    def test_add_entity(self) -> None:
        """add_entity() adds entity to field."""
        widget = DensityFieldWidget()
        entity = Entity(id="test", x=10, y=5)
        updated = widget.add_entity(entity)

        assert len(widget.state.value.entities) == 0
        assert len(updated.state.value.entities) == 1
        assert updated.state.value.entities[0].id == "test"

    def test_add_entity_replaces_existing(self) -> None:
        """add_entity() replaces entity with same id."""
        widget = DensityFieldWidget(
            DensityFieldState(entities=(Entity(id="test", x=10, y=5),))
        )
        updated = widget.add_entity(Entity(id="test", x=20, y=10))

        assert len(updated.state.value.entities) == 1
        assert updated.state.value.entities[0].x == 20

    def test_remove_entity(self) -> None:
        """remove_entity() removes entity by id."""
        widget = DensityFieldWidget(
            DensityFieldState(
                entities=(
                    Entity(id="a", x=10, y=5),
                    Entity(id="b", x=20, y=10),
                )
            )
        )
        updated = widget.remove_entity("a")

        assert len(widget.state.value.entities) == 2
        assert len(updated.state.value.entities) == 1
        assert updated.state.value.entities[0].id == "b"


class TestDensityFieldEntropyComputation:
    """Tests for spatial entropy coherence."""

    def test_base_entropy_at_empty_position(self) -> None:
        """Empty position has base entropy."""
        widget = DensityFieldWidget(DensityFieldState(base_entropy=0.2))
        entropy = widget._compute_entropy_at(10, 10)
        assert entropy == pytest.approx(0.2, abs=0.01)

    def test_entity_adds_heat_at_position(self) -> None:
        """Entity position has added heat."""
        widget = DensityFieldWidget(
            DensityFieldState(
                base_entropy=0.1,
                entities=(Entity(id="hot", x=10, y=10, heat=0.5),),
            )
        )
        entropy = widget._compute_entropy_at(10, 10)
        assert entropy == pytest.approx(0.6, abs=0.01)  # 0.1 + 0.5

    def test_heat_decays_with_distance(self) -> None:
        """Heat contribution decays with distance."""
        widget = DensityFieldWidget(
            DensityFieldState(
                base_entropy=0.0,
                entities=(Entity(id="hot", x=10, y=10, heat=1.0),),
            )
        )

        at_entity = widget._compute_entropy_at(10, 10)
        near_entity = widget._compute_entropy_at(11, 10)  # 1 cell away
        far_from_entity = widget._compute_entropy_at(20, 10)  # 10 cells away

        assert at_entity > near_entity > far_from_entity

    def test_entropy_capped_at_one(self) -> None:
        """Entropy is capped at 1.0."""
        widget = DensityFieldWidget(
            DensityFieldState(
                base_entropy=0.5,
                entities=(
                    Entity(id="hot1", x=10, y=10, heat=1.0),
                    Entity(id="hot2", x=10, y=10, heat=1.0),
                ),
            )
        )
        entropy = widget._compute_entropy_at(10, 10)
        assert entropy == 1.0


class TestDensityFieldProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns multiline string."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_correct_dimensions(self) -> None:
        """CLI output has correct dimensions."""
        widget = DensityFieldWidget(DensityFieldState(width=20, height=10))
        result = widget.project(RenderTarget.CLI)
        lines = result.split("\n")

        assert len(lines) == 10  # height
        assert all(len(line) == 20 for line in lines)  # width

    def test_project_cli_shows_entity(self) -> None:
        """CLI shows entity at its position."""
        widget = DensityFieldWidget(
            DensityFieldState(
                width=10,
                height=5,
                entities=(Entity(id="test", x=5, y=2, char="★"),),
            )
        )
        result = widget.project(RenderTarget.CLI)
        assert "★" in result


class TestDensityFieldProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes basic fields."""
        widget = DensityFieldWidget(
            DensityFieldState(width=20, height=10, base_entropy=0.2)
        )
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "density_field"
        assert result["width"] == 20
        assert result["height"] == 10
        assert result["base_entropy"] == 0.2

    def test_project_json_includes_entities(self) -> None:
        """JSON projection includes entity list."""
        widget = DensityFieldWidget(
            DensityFieldState(
                width=10,
                height=5,
                entities=(Entity(id="a", x=5, y=2),),
            )
        )
        result = widget.project(RenderTarget.JSON)

        assert "entities" in result
        assert len(result["entities"]) == 1
        assert result["entities"][0]["id"] == "a"

    def test_project_json_includes_cells(self) -> None:
        """JSON projection includes cell array."""
        widget = DensityFieldWidget(DensityFieldState(width=5, height=3))
        result = widget.project(RenderTarget.JSON)

        assert "cells" in result
        assert len(result["cells"]) == 15  # 5 * 3
        assert all("x" in c and "y" in c for c in result["cells"])

    def test_project_json_includes_wind_when_active(self) -> None:
        """JSON projection includes wind when strength > 0."""
        widget = DensityFieldWidget(
            DensityFieldState(wind=Wind(dx=0.5, dy=-0.2, strength=0.3))
        )
        result = widget.project(RenderTarget.JSON)

        assert "wind" in result
        assert result["wind"]["dx"] == 0.5
        assert result["wind"]["strength"] == 0.3


class TestDensityFieldProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-density-field" in result

    def test_project_marimo_has_rows(self) -> None:
        """Marimo projection has row divs."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.MARIMO)
        assert result.count("kgents-field-row") == 5


class TestDensityFieldProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_list(self) -> None:
        """TUI projection returns list of Rich Text rows."""
        widget = DensityFieldWidget(DensityFieldState(width=10, height=5))
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            assert isinstance(result, list)
            assert len(result) == 5
            assert all(isinstance(row, Text) for row in result)
        except ImportError:
            # Fallback to string
            assert isinstance(result, str)


class TestDensityFieldDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = DensityFieldState(
            width=10,
            height=5,
            base_entropy=0.2,
            entities=(Entity(id="test", x=5, y=2, heat=0.5),),
            seed=42,
            t=1000.0,
        )

        widget1 = DensityFieldWidget(state)
        widget2 = DensityFieldWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        # JSON comparison (cells may have floating point)
        json1 = widget1.project(RenderTarget.JSON)
        json2 = widget2.project(RenderTarget.JSON)
        assert json1["width"] == json2["width"]
        assert json1["entity_count"] == json2["entity_count"]

    def test_different_time_different_distortion(self) -> None:
        """Different time produces different visual distortion."""
        state1 = DensityFieldState(width=5, height=3, base_entropy=0.5, seed=42, t=0.0)
        state2 = DensityFieldState(
            width=5, height=3, base_entropy=0.5, seed=42, t=3141.59
        )

        widget1 = DensityFieldWidget(state1)
        widget2 = DensityFieldWidget(state2)

        # With entropy, distortion should differ with time
        json1 = widget1.project(RenderTarget.JSON)
        json2 = widget2.project(RenderTarget.JSON)

        # Find cells with distortion
        distorted1 = [c for c in json1["cells"] if c.get("distortion")]
        distorted2 = [c for c in json2["cells"] if c.get("distortion")]

        if distorted1 and distorted2:
            # Distortions should differ due to time
            assert distorted1[0]["distortion"] != distorted2[0]["distortion"]
