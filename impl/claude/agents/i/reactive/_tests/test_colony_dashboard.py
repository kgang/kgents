"""
Tests for ColonyDashboard.

Wave 4 Test Suite
=================

Tests verify:
1. ColonyState creation and field handling
2. Grid composition with CitizenWidgets
3. All projection targets (CLI/TUI/marimo/JSON)
4. Citizen selection
5. Signal binding for reactive updates
6. Performance with many citizens
"""

from __future__ import annotations

import time
from typing import Any

import pytest
from agents.i.reactive.colony_dashboard import (
    ColonyDashboard,
    ColonyState,
    TownPhase,
)
from agents.i.reactive.primitives.citizen_card import CitizenState
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import RenderTarget
from agents.town.polynomial import CitizenPhase
from protocols.nphase.operad import NPhase

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_citizens() -> tuple[CitizenState, ...]:
    """Create sample citizens for testing."""
    return (
        CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.WORKING,
            nphase=NPhase.ACT,
            capability=0.85,
            mood="focused",
        ),
        CitizenState(
            citizen_id="bob",
            name="Bob",
            archetype="trader",
            phase=CitizenPhase.IDLE,
            nphase=NPhase.SENSE,
            capability=0.92,
            mood="calm",
        ),
        CitizenState(
            citizen_id="carol",
            name="Carol",
            archetype="healer",
            phase=CitizenPhase.REFLECTING,
            nphase=NPhase.REFLECT,
            capability=0.78,
            mood="contemplative",
        ),
    )


@pytest.fixture
def sample_colony(sample_citizens: tuple[CitizenState, ...]) -> ColonyState:
    """Create sample colony state."""
    return ColonyState(
        colony_id="test-colony-1",
        citizens=sample_citizens,
        phase=TownPhase.AFTERNOON,
        day=3,
        total_events=42,
        total_tokens=1500,
        entropy_budget=0.75,
    )


# =============================================================================
# ColonyState Tests
# =============================================================================


class TestColonyState:
    """Tests for ColonyState dataclass."""

    def test_default_values(self) -> None:
        """Test default ColonyState values."""
        state = ColonyState()
        assert state.colony_id == ""
        assert state.citizens == ()
        assert state.phase == TownPhase.MORNING
        assert state.day == 1
        assert state.total_events == 0
        assert state.total_tokens == 0
        assert state.entropy_budget == 1.0
        assert state.selected_citizen_id is None
        assert state.grid_cols == 4

    def test_custom_values(self, sample_citizens: tuple[CitizenState, ...]) -> None:
        """Test ColonyState with custom values."""
        state = ColonyState(
            colony_id="my-colony",
            citizens=sample_citizens,
            phase=TownPhase.EVENING,
            day=5,
            total_events=100,
            total_tokens=5000,
            entropy_budget=0.5,
            selected_citizen_id="alice",
            grid_cols=3,
        )
        assert state.colony_id == "my-colony"
        assert len(state.citizens) == 3
        assert state.phase == TownPhase.EVENING
        assert state.day == 5
        assert state.total_events == 100
        assert state.total_tokens == 5000
        assert state.entropy_budget == 0.5
        assert state.selected_citizen_id == "alice"
        assert state.grid_cols == 3

    def test_frozen_immutability(self, sample_colony: ColonyState) -> None:
        """Test that ColonyState is immutable."""
        with pytest.raises(Exception):
            sample_colony.day = 10  # type: ignore[misc]


class TestTownPhase:
    """Tests for TownPhase enum."""

    def test_all_phases_exist(self) -> None:
        """Test all expected phases exist."""
        phases = [
            TownPhase.MORNING,
            TownPhase.AFTERNOON,
            TownPhase.EVENING,
            TownPhase.NIGHT,
        ]
        assert len(phases) == 4

    def test_phase_names(self) -> None:
        """Test phase name strings."""
        assert TownPhase.MORNING.name == "MORNING"
        assert TownPhase.AFTERNOON.name == "AFTERNOON"
        assert TownPhase.EVENING.name == "EVENING"
        assert TownPhase.NIGHT.name == "NIGHT"


# =============================================================================
# ColonyDashboard Tests
# =============================================================================


class TestColonyDashboard:
    """Tests for ColonyDashboard widget."""

    def test_creation_default(self) -> None:
        """Test dashboard creation with defaults."""
        dashboard = ColonyDashboard()
        assert dashboard.state.value.colony_id == ""
        assert dashboard.state.value.citizens == ()

    def test_creation_with_state(self, sample_colony: ColonyState) -> None:
        """Test dashboard creation with custom state."""
        dashboard = ColonyDashboard(sample_colony)
        assert dashboard.state.value.colony_id == "test-colony-1"
        assert len(dashboard.state.value.citizens) == 3

    def test_with_state_immutable(self, sample_colony: ColonyState) -> None:
        """Test that with_state returns new dashboard."""
        dashboard1 = ColonyDashboard(sample_colony)
        dashboard2 = dashboard1.with_state(ColonyState(colony_id="other"))

        assert dashboard1.state.value.colony_id == "test-colony-1"
        assert dashboard2.state.value.colony_id == "other"
        assert dashboard1 is not dashboard2

    def test_select_citizen(self, sample_colony: ColonyState) -> None:
        """Test citizen selection."""
        dashboard = ColonyDashboard(sample_colony)
        selected = dashboard.select_citizen("alice")

        assert dashboard.state.value.selected_citizen_id is None
        assert selected.state.value.selected_citizen_id == "alice"

    def test_set_grid_cols(self, sample_colony: ColonyState) -> None:
        """Test grid column configuration."""
        dashboard = ColonyDashboard(sample_colony)
        modified = dashboard.set_grid_cols(6)

        assert dashboard.state.value.grid_cols == 4
        assert modified.state.value.grid_cols == 6

    def test_set_grid_cols_minimum(self, sample_colony: ColonyState) -> None:
        """Test grid column minimum is 1."""
        dashboard = ColonyDashboard(sample_colony)
        modified = dashboard.set_grid_cols(0)

        assert modified.state.value.grid_cols == 1


class TestColonyDashboardGrid:
    """Tests for grid composition."""

    def test_empty_grid(self) -> None:
        """Test dashboard with no citizens."""
        dashboard = ColonyDashboard(ColonyState())
        grid = dashboard._build_citizen_grid()
        assert grid is None

    def test_single_citizen_grid(self) -> None:
        """Test dashboard with single citizen."""
        state = ColonyState(citizens=(CitizenState(citizen_id="alice", name="Alice"),))
        dashboard = ColonyDashboard(state)
        grid = dashboard._build_citizen_grid()

        # Single citizen should create a row
        assert grid is not None

    def test_full_row_grid(self, sample_citizens: tuple[CitizenState, ...]) -> None:
        """Test dashboard with citizens fitting in one row."""
        state = ColonyState(citizens=sample_citizens, grid_cols=4)
        dashboard = ColonyDashboard(state)
        grid = dashboard._build_citizen_grid()

        assert grid is not None

    def test_multiple_rows_grid(self) -> None:
        """Test dashboard with multiple rows."""
        citizens = tuple(
            CitizenState(citizen_id=f"citizen-{i}", name=f"Citizen {i}")
            for i in range(8)
        )
        state = ColonyState(citizens=citizens, grid_cols=4)
        dashboard = ColonyDashboard(state)
        grid = dashboard._build_citizen_grid()

        assert grid is not None
        # 8 citizens / 4 cols = 2 rows
        from agents.i.reactive.composable import VStack

        assert isinstance(grid, VStack)


# =============================================================================
# CLI Projection Tests
# =============================================================================


class TestColonyDashboardCLI:
    """Tests for CLI projection."""

    def test_project_cli_structure(self, sample_colony: ColonyState) -> None:
        """Test CLI projection structure."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.CLI)

        assert "AGENT TOWN DASHBOARD" in output
        assert "test-colony" in output  # May be truncated
        assert "Citizens:" in output
        assert "AFTERNOON" in output
        assert "Day:" in output  # Value may be truncated due to fixed width

    def test_project_cli_citizens(self, sample_colony: ColonyState) -> None:
        """Test CLI projection includes citizen names."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.CLI)

        assert "Alice" in output
        assert "Bob" in output
        assert "Carol" in output

    def test_project_cli_metrics(self, sample_colony: ColonyState) -> None:
        """Test CLI projection includes metrics."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.CLI)

        assert "Entropy: 0.75" in output
        assert "Events: 42" in output
        assert "Tokens: 1500" in output

    def test_project_cli_empty(self) -> None:
        """Test CLI projection with no citizens."""
        dashboard = ColonyDashboard(ColonyState())
        output = dashboard.project(RenderTarget.CLI)

        assert "AGENT TOWN DASHBOARD" in output
        assert "(no citizens)" in output

    def test_project_cli_box_drawing(self, sample_colony: ColonyState) -> None:
        """Test CLI projection uses box drawing characters."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.CLI)

        assert "┌" in output
        assert "─" in output
        assert "┐" in output
        assert "│" in output
        assert "└" in output
        assert "┘" in output


# =============================================================================
# marimo Projection Tests
# =============================================================================


class TestColonyDashboardMarimo:
    """Tests for marimo projection."""

    def test_project_marimo_html_structure(self, sample_colony: ColonyState) -> None:
        """Test marimo projection returns valid HTML."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.MARIMO)

        assert isinstance(output, str)
        assert 'class="kgents-colony-dashboard"' in output
        assert 'data-colony-id="test-colony-1"' in output
        assert "AGENT TOWN DASHBOARD" in output

    def test_project_marimo_includes_status(self, sample_colony: ColonyState) -> None:
        """Test marimo projection includes status information."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.MARIMO)

        assert "test-colony-1" in output
        assert "Citizens:" in output
        assert "AFTERNOON" in output
        assert "Day 3" in output

    def test_project_marimo_includes_footer(self, sample_colony: ColonyState) -> None:
        """Test marimo projection includes footer metrics."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.MARIMO)

        assert "Entropy: 0.75" in output
        assert "Tokens: 1500" in output


# =============================================================================
# JSON Projection Tests
# =============================================================================


class TestColonyDashboardJSON:
    """Tests for JSON projection."""

    def test_project_json_structure(self, sample_colony: ColonyState) -> None:
        """Test JSON projection returns correct structure."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.JSON)

        assert output["type"] == "colony_dashboard"
        assert output["colony_id"] == "test-colony-1"
        assert output["phase"] == "AFTERNOON"
        assert output["day"] == 3

    def test_project_json_metrics(self, sample_colony: ColonyState) -> None:
        """Test JSON projection includes metrics."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.JSON)

        assert "metrics" in output
        assert output["metrics"]["total_events"] == 42
        assert output["metrics"]["total_tokens"] == 1500
        assert output["metrics"]["entropy_budget"] == 0.75

    def test_project_json_citizens(self, sample_colony: ColonyState) -> None:
        """Test JSON projection includes citizens."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.JSON)

        assert "citizens" in output
        assert len(output["citizens"]) == 3

        alice = output["citizens"][0]
        assert alice["citizen_id"] == "alice"
        assert alice["name"] == "Alice"
        assert alice["archetype"] == "builder"
        assert alice["phase"] == "WORKING"
        assert alice["nphase"] == "ACT"
        # Verify eigenvectors are included
        assert "eigenvectors" in alice
        assert "warmth" in alice["eigenvectors"]
        assert "curiosity" in alice["eigenvectors"]
        assert "trust" in alice["eigenvectors"]

    def test_project_json_grid_config(self, sample_colony: ColonyState) -> None:
        """Test JSON projection includes grid configuration."""
        dashboard = ColonyDashboard(sample_colony)
        output = dashboard.project(RenderTarget.JSON)

        assert output["grid_cols"] == 4
        assert output["selected_citizen_id"] is None


# =============================================================================
# Signal Binding Tests
# =============================================================================


class TestColonyDashboardSignal:
    """Tests for Signal binding."""

    def test_bind_signal_updates_state(
        self, sample_citizens: tuple[CitizenState, ...]
    ) -> None:
        """Test that bound signal updates dashboard state."""
        initial = ColonyState(colony_id="initial")
        updated = ColonyState(colony_id="updated", citizens=sample_citizens)

        signal = Signal.of(initial)
        dashboard = ColonyDashboard()
        dashboard.bind_signal(signal)

        # Initial state should be dashboard default
        assert dashboard.state.value.colony_id == ""

        # Update signal
        signal.set(updated)

        # Dashboard should reflect new state
        assert dashboard.state.value.colony_id == "updated"
        assert len(dashboard.state.value.citizens) == 3


# =============================================================================
# Performance Tests
# =============================================================================


class TestColonyDashboardPerformance:
    """Performance tests for dashboard."""

    def test_render_25_citizens_performance(self) -> None:
        """Test rendering 25 citizens is fast (<50ms)."""
        citizens = tuple(
            CitizenState(
                citizen_id=f"citizen-{i}",
                name=f"Citizen {i}",
                archetype="builder",
                phase=CitizenPhase.IDLE,
            )
            for i in range(25)
        )
        state = ColonyState(colony_id="perf-test", citizens=citizens)
        dashboard = ColonyDashboard(state)

        start = time.perf_counter()
        for _ in range(10):
            dashboard.project(RenderTarget.CLI)
        elapsed = (time.perf_counter() - start) / 10 * 1000  # ms

        assert elapsed < 50, f"Render took {elapsed:.2f}ms, expected <50ms"

    def test_composition_50_citizens(self) -> None:
        """Test grid composition with 50 citizens."""
        citizens = tuple(
            CitizenState(citizen_id=f"c-{i}", name=f"C{i}") for i in range(50)
        )
        state = ColonyState(citizens=citizens, grid_cols=5)
        dashboard = ColonyDashboard(state)

        # Should complete without error
        grid = dashboard._build_citizen_grid()
        assert grid is not None

        # JSON projection should list all citizens
        json = dashboard.project(RenderTarget.JSON)
        assert len(json["citizens"]) == 50

    def test_stress_100_renders(self, sample_colony: ColonyState) -> None:
        """Test 100 renders complete in reasonable time."""
        dashboard = ColonyDashboard(sample_colony)

        start = time.perf_counter()
        for _ in range(100):
            dashboard.project(RenderTarget.JSON)
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"100 renders took {elapsed:.2f}s, expected <2s"


# =============================================================================
# Composition Tests
# =============================================================================


class TestColonyDashboardComposition:
    """Tests for >> and // composition operators."""

    def test_dashboard_horizontal_composition(self, sample_colony: ColonyState) -> None:
        """Test dashboard can be composed horizontally."""
        from agents.i.reactive.composable import HStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        dashboard = ColonyDashboard(sample_colony)
        status = GlyphWidget(GlyphState(char="●"))

        result = status >> dashboard

        assert isinstance(result, HStack)

    def test_dashboard_vertical_composition(self, sample_colony: ColonyState) -> None:
        """Test dashboard can be composed vertically."""
        from agents.i.reactive.composable import VStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        dashboard = ColonyDashboard(sample_colony)
        header = GlyphWidget(GlyphState(char="★"))

        result = header // dashboard

        assert isinstance(result, VStack)
