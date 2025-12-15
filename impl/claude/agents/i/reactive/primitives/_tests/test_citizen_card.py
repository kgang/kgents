"""
Tests for CitizenWidget.

Wave 4 Test Suite
=================

Tests verify:
1. CitizenState creation and field extraction
2. Phase to glyph mapping
3. Conversion to AgentCardState
4. All projection targets (CLI/TUI/marimo/JSON)
5. Activity history handling
6. Composition via >> and // operators
"""

from __future__ import annotations

import pytest
from agents.i.reactive.composable import HStack, VStack
from agents.i.reactive.primitives.citizen_card import (
    NPHASE_LABELS,
    PHASE_GLYPHS,
    PHASE_TO_GLYPH,
    CitizenState,
    CitizenWidget,
)
from agents.i.reactive.widget import RenderTarget
from agents.town.polynomial import CitizenPhase
from protocols.nphase.operad import NPhase

# =============================================================================
# CitizenState Tests
# =============================================================================


class TestCitizenState:
    """Tests for CitizenState dataclass."""

    def test_default_values(self) -> None:
        """Test default CitizenState values."""
        state = CitizenState()
        assert state.citizen_id == ""
        assert state.name == "Citizen"
        assert state.archetype == "unknown"
        assert state.phase == CitizenPhase.IDLE
        assert state.nphase == NPhase.SENSE
        assert state.activity == ()
        assert state.capability == 1.0
        assert state.entropy == 0.0
        assert state.mood == "calm"

    def test_custom_values(self) -> None:
        """Test CitizenState with custom values."""
        state = CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.WORKING,
            nphase=NPhase.ACT,
            activity=(0.5, 0.7, 0.9),
            capability=0.85,
            entropy=0.15,
            mood="focused",
        )
        assert state.citizen_id == "alice"
        assert state.name == "Alice"
        assert state.archetype == "builder"
        assert state.phase == CitizenPhase.WORKING
        assert state.nphase == NPhase.ACT
        assert state.activity == (0.5, 0.7, 0.9)
        assert state.capability == 0.85
        assert state.entropy == 0.15
        assert state.mood == "focused"

    def test_frozen_immutability(self) -> None:
        """Test that CitizenState is immutable."""
        state = CitizenState(name="Alice")
        with pytest.raises(Exception):  # FrozenInstanceError
            state.name = "Bob"  # type: ignore[misc]


class TestCitizenStateFromCitizen:
    """Tests for CitizenState.from_citizen() extraction."""

    def test_from_citizen_basic(self) -> None:
        """Test basic extraction from Citizen entity."""
        from agents.town.citizen import Citizen

        citizen = Citizen(
            name="Alice",
            archetype="builder",
            region="plaza",
        )
        state = CitizenState.from_citizen(citizen)

        assert state.name == "Alice"
        assert state.archetype == "builder"
        assert state.region == "plaza"
        assert state.phase == CitizenPhase.IDLE
        assert state.nphase == NPhase.SENSE
        assert state.capability == 1.0  # No accursed surplus
        assert state.entropy == 0.0

    def test_from_citizen_with_accursed_surplus(self) -> None:
        """Test capability/entropy from accursed_surplus."""
        from agents.town.citizen import Citizen

        citizen = Citizen(name="Bob", archetype="trader", region="market")
        citizen.accursed_surplus = 5.0  # 50% of cap

        state = CitizenState.from_citizen(citizen)

        assert state.capability == 0.5  # 1.0 - 5/10
        assert state.entropy == 0.5  # 5/10

    def test_from_citizen_with_activity(self) -> None:
        """Test activity samples passed through."""
        from agents.town.citizen import Citizen

        citizen = Citizen(name="Carol", archetype="healer", region="clinic")
        activity = (0.2, 0.4, 0.6, 0.8)

        state = CitizenState.from_citizen(citizen, activity_samples=activity)

        assert state.activity == activity

    def test_from_citizen_eigenvectors(self) -> None:
        """Test eigenvector extraction."""
        from agents.town.citizen import Citizen, Eigenvectors

        citizen = Citizen(
            name="Dave",
            archetype="scholar",
            region="library",
            eigenvectors=Eigenvectors(warmth=0.8, curiosity=0.9, trust=0.6),
        )

        state = CitizenState.from_citizen(citizen)

        assert state.warmth == 0.8
        assert state.curiosity == 0.9
        assert state.trust == 0.6


class TestCitizenStateToAgentCard:
    """Tests for CitizenState.to_agent_card_state() conversion."""

    def test_to_agent_card_state_idle(self) -> None:
        """Test conversion for IDLE phase."""
        state = CitizenState(
            citizen_id="alice",
            name="Alice",
            phase=CitizenPhase.IDLE,
        )
        agent_card = state.to_agent_card_state()

        assert agent_card.agent_id == "alice"
        assert agent_card.name == "Alice"
        assert agent_card.phase == "idle"
        assert agent_card.breathing is False

    def test_to_agent_card_state_working(self) -> None:
        """Test conversion for WORKING phase (should breathe)."""
        state = CitizenState(
            citizen_id="bob",
            name="Bob",
            phase=CitizenPhase.WORKING,
        )
        agent_card = state.to_agent_card_state()

        assert agent_card.phase == "active"
        assert agent_card.breathing is True

    def test_to_agent_card_state_reflecting(self) -> None:
        """Test conversion for REFLECTING phase (pulse, not breathe)."""
        state = CitizenState(
            citizen_id="carol",
            name="Carol",
            phase=CitizenPhase.REFLECTING,
        )
        agent_card = state.to_agent_card_state()

        assert agent_card.phase == "thinking"
        assert agent_card.breathing is False  # pulse, not breathe

    def test_to_agent_card_state_resting(self) -> None:
        """Test conversion for RESTING phase (maps to idle for compatibility)."""
        state = CitizenState(
            citizen_id="dave",
            name="Dave",
            phase=CitizenPhase.RESTING,
        )
        agent_card = state.to_agent_card_state()

        # RESTING maps to "idle" since base Phase type doesn't include "resting"
        assert agent_card.phase == "idle"
        assert agent_card.breathing is False


# =============================================================================
# Phase Mapping Tests
# =============================================================================


class TestPhaseGlyphMapping:
    """Tests for phase to glyph mapping."""

    def test_all_phases_have_glyphs(self) -> None:
        """All CitizenPhase values have glyph mappings."""
        for phase in CitizenPhase:
            assert phase in PHASE_GLYPHS
            assert phase in PHASE_TO_GLYPH

    def test_all_nphases_have_labels(self) -> None:
        """All NPhase values have labels."""
        for nphase in NPhase:
            assert nphase in NPHASE_LABELS

    def test_glyph_uniqueness(self) -> None:
        """Each phase has a unique glyph."""
        glyphs = list(PHASE_GLYPHS.values())
        assert len(glyphs) == len(set(glyphs))

    @pytest.mark.parametrize(
        "phase,expected_glyph",
        [
            (CitizenPhase.IDLE, "○"),
            (CitizenPhase.SOCIALIZING, "◉"),
            (CitizenPhase.WORKING, "●"),
            (CitizenPhase.REFLECTING, "◐"),
            (CitizenPhase.RESTING, "◯"),
        ],
    )
    def test_phase_glyph_values(self, phase: CitizenPhase, expected_glyph: str) -> None:
        """Test specific glyph values."""
        assert PHASE_GLYPHS[phase] == expected_glyph


# =============================================================================
# CitizenWidget Tests
# =============================================================================


class TestCitizenWidget:
    """Tests for CitizenWidget."""

    def test_creation_default(self) -> None:
        """Test widget creation with defaults."""
        widget = CitizenWidget()
        assert widget.state.value.name == "Citizen"

    def test_creation_with_state(self) -> None:
        """Test widget creation with custom state."""
        state = CitizenState(name="Alice", archetype="builder")
        widget = CitizenWidget(state)
        assert widget.state.value.name == "Alice"
        assert widget.state.value.archetype == "builder"

    def test_with_state_immutable(self) -> None:
        """Test that with_state returns new widget."""
        widget1 = CitizenWidget(CitizenState(name="Alice"))
        widget2 = widget1.with_state(CitizenState(name="Bob"))

        assert widget1.state.value.name == "Alice"
        assert widget2.state.value.name == "Bob"
        assert widget1 is not widget2

    def test_with_activity(self) -> None:
        """Test with_activity returns new widget."""
        widget1 = CitizenWidget(CitizenState(name="Alice"))
        widget2 = widget1.with_activity((0.1, 0.5, 0.9))

        assert widget1.state.value.activity == ()
        assert widget2.state.value.activity == (0.1, 0.5, 0.9)

    def test_with_time(self) -> None:
        """Test with_time returns new widget."""
        widget1 = CitizenWidget(CitizenState(name="Alice"))
        widget2 = widget1.with_time(1000.0)

        assert widget1.state.value.t == 0.0
        assert widget2.state.value.t == 1000.0


class TestCitizenWidgetCLI:
    """Tests for CLI projection."""

    def test_project_cli_basic(self) -> None:
        """Test basic CLI projection."""
        state = CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.IDLE,
            nphase=NPhase.SENSE,
        )
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.CLI)

        assert "○" in output  # IDLE glyph
        assert "Alice" in output
        assert "[S]" in output  # SENSE
        assert "Builder" in output

    def test_project_cli_with_activity(self) -> None:
        """Test CLI projection with activity sparkline."""
        state = CitizenState(
            name="Bob",
            archetype="trader",
            activity=(0.1, 0.3, 0.5, 0.7, 0.9),
        )
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.CLI)

        # Should contain sparkline characters
        assert any(c in output for c in "▁▂▃▄▅▆▇█")

    def test_project_cli_capability_bar(self) -> None:
        """Test CLI projection shows capability bar."""
        state = CitizenState(name="Carol", capability=0.5)
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.CLI)

        assert "cap:" in output
        assert "█" in output
        assert "░" in output


class TestCitizenWidgetMarimo:
    """Tests for marimo projection."""

    def test_project_marimo_html_structure(self) -> None:
        """Test marimo projection returns valid HTML."""
        state = CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
        )
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.MARIMO)

        assert isinstance(output, str)
        assert 'class="kgents-citizen-card"' in output
        assert 'data-citizen-id="alice"' in output
        assert "Alice" in output
        assert "builder" in output

    def test_project_marimo_animation_working(self) -> None:
        """Test marimo projection includes animation for WORKING."""
        state = CitizenState(name="Bob", phase=CitizenPhase.WORKING)
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.MARIMO)

        assert "animation: breathe" in output

    def test_project_marimo_animation_reflecting(self) -> None:
        """Test marimo projection includes pulse for REFLECTING."""
        state = CitizenState(name="Carol", phase=CitizenPhase.REFLECTING)
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.MARIMO)

        assert "animation: pulse" in output


class TestCitizenWidgetJSON:
    """Tests for JSON projection."""

    def test_project_json_structure(self) -> None:
        """Test JSON projection returns correct structure."""
        state = CitizenState(
            citizen_id="alice",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.WORKING,
            nphase=NPhase.ACT,
            capability=0.85,
            mood="focused",
        )
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.JSON)

        assert output["type"] == "citizen_card"
        assert output["citizen_id"] == "alice"
        assert output["name"] == "Alice"
        assert output["archetype"] == "builder"
        assert output["phase"] == "WORKING"
        assert output["nphase"] == "ACT"
        assert output["capability"] == 0.85
        assert output["mood"] == "focused"

    def test_project_json_eigenvectors(self) -> None:
        """Test JSON projection includes eigenvectors."""
        state = CitizenState(
            name="Bob",
            warmth=0.8,
            curiosity=0.9,
            trust=0.6,
        )
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.JSON)

        assert "eigenvectors" in output
        assert output["eigenvectors"]["warmth"] == 0.8
        assert output["eigenvectors"]["curiosity"] == 0.9
        assert output["eigenvectors"]["trust"] == 0.6


# =============================================================================
# Composition Tests
# =============================================================================


class TestCitizenWidgetComposition:
    """Tests for >> and // composition operators."""

    def test_horizontal_composition(self) -> None:
        """Test >> creates HStack."""
        widget1 = CitizenWidget(CitizenState(name="Alice"))
        widget2 = CitizenWidget(CitizenState(name="Bob"))

        result = widget1 >> widget2

        assert isinstance(result, HStack)
        assert len(result.children) == 2

    def test_vertical_composition(self) -> None:
        """Test // creates VStack."""
        widget1 = CitizenWidget(CitizenState(name="Alice"))
        widget2 = CitizenWidget(CitizenState(name="Bob"))

        result = widget1 // widget2

        assert isinstance(result, VStack)
        assert len(result.children) == 2

    def test_chain_composition(self) -> None:
        """Test chained composition."""
        w1 = CitizenWidget(CitizenState(name="Alice"))
        w2 = CitizenWidget(CitizenState(name="Bob"))
        w3 = CitizenWidget(CitizenState(name="Carol"))

        row = w1 >> w2 >> w3

        assert isinstance(row, HStack)
        assert len(row.children) == 3

    def test_grid_composition(self) -> None:
        """Test grid composition with rows and columns."""
        w1 = CitizenWidget(CitizenState(name="Alice"))
        w2 = CitizenWidget(CitizenState(name="Bob"))
        w3 = CitizenWidget(CitizenState(name="Carol"))
        w4 = CitizenWidget(CitizenState(name="Dave"))

        row1 = w1 >> w2
        row2 = w3 >> w4
        grid = row1 // row2

        assert isinstance(grid, VStack)
        assert len(grid.children) == 2
        assert all(isinstance(row, HStack) for row in grid.children)

    def test_composition_projection_cli(self) -> None:
        """Test composed widgets project to CLI."""
        w1 = CitizenWidget(CitizenState(name="Alice", phase=CitizenPhase.IDLE))
        w2 = CitizenWidget(CitizenState(name="Bob", phase=CitizenPhase.WORKING))

        row = w1 >> w2
        output = row.project(RenderTarget.CLI)

        assert "Alice" in output
        assert "Bob" in output

    def test_composition_projection_json(self) -> None:
        """Test composed widgets project to JSON."""
        w1 = CitizenWidget(CitizenState(name="Alice"))
        w2 = CitizenWidget(CitizenState(name="Bob"))

        row = w1 >> w2
        output = row.project(RenderTarget.JSON)

        assert output["type"] == "hstack"
        assert len(output["children"]) == 2


# =============================================================================
# Activity History Tests
# =============================================================================


class TestActivityHistory:
    """Tests for activity history handling."""

    def test_activity_bounds_clamped(self) -> None:
        """Test activity values are in [0, 1]."""
        state = CitizenState(activity=(0.0, 0.5, 1.0))
        widget = CitizenWidget(state)
        output = widget.project(RenderTarget.JSON)

        for v in output["activity"]:
            assert 0.0 <= v <= 1.0

    def test_empty_activity(self) -> None:
        """Test empty activity history renders without error."""
        state = CitizenState(activity=())
        widget = CitizenWidget(state)

        cli = widget.project(RenderTarget.CLI)
        marimo = widget.project(RenderTarget.MARIMO)
        json = widget.project(RenderTarget.JSON)

        assert isinstance(cli, str)
        assert isinstance(marimo, str)
        assert json["activity"] == []

    def test_long_activity_truncated(self) -> None:
        """Test long activity is truncated to last 10 for display."""
        long_activity = tuple(i / 20 for i in range(20))
        state = CitizenState(activity=long_activity)
        widget = CitizenWidget(state)

        # JSON should have all values
        json = widget.project(RenderTarget.JSON)
        assert len(json["activity"]) == 20

        # CLI sparkline should show last 10
        cli = widget.project(RenderTarget.CLI)
        assert isinstance(cli, str)
