"""
Tests for live.state SSE event emission.

Phase 3: SSE Integration
========================

Tests the should_emit_state() and build_colony_dashboard() helper functions
that power the `live.state` SSE event emission.

Test Categories:
- TestShouldEmitState: Emission trigger logic
- TestBuildColonyDashboard: Dashboard construction from environment
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from protocols.api.town import build_colony_dashboard, should_emit_state

# =============================================================================
# TestShouldEmitState
# =============================================================================


class TestShouldEmitState:
    """Tests for should_emit_state() emission logic."""

    def test_emits_every_5_ticks(self) -> None:
        """Should emit on tick multiples of 5."""
        mock_event = MagicMock(operation="greet")
        assert should_emit_state(5, mock_event) is True
        assert should_emit_state(10, mock_event) is True
        assert should_emit_state(15, mock_event) is True
        assert should_emit_state(100, mock_event) is True

    def test_does_not_emit_on_non_5_ticks(self) -> None:
        """Should not emit on non-5 ticks with normal operations."""
        mock_event = MagicMock(operation="greet")
        assert should_emit_state(1, mock_event) is False
        assert should_emit_state(3, mock_event) is False
        assert should_emit_state(7, mock_event) is False
        assert should_emit_state(99, mock_event) is False

    def test_emits_on_evolve_operation(self) -> None:
        """Should emit on 'evolve' operation regardless of tick."""
        mock_event = MagicMock(operation="evolve")
        assert should_emit_state(1, mock_event) is True
        assert should_emit_state(3, mock_event) is True

    def test_emits_on_coalition_formed(self) -> None:
        """Should emit on 'coalition_formed' operation."""
        mock_event = MagicMock(operation="coalition_formed")
        assert should_emit_state(1, mock_event) is True

    def test_emits_on_coalition_dissolved(self) -> None:
        """Should emit on 'coalition_dissolved' operation."""
        mock_event = MagicMock(operation="coalition_dissolved")
        assert should_emit_state(2, mock_event) is True

    def test_does_not_emit_on_normal_operations(self) -> None:
        """Should not emit on normal operations at non-5 ticks."""
        for operation in ["greet", "gossip", "trade", "rest", "move"]:
            mock_event = MagicMock(operation=operation)
            assert should_emit_state(3, mock_event) is False


# =============================================================================
# TestBuildColonyDashboard
# =============================================================================


class TestBuildColonyDashboard:
    """Tests for build_colony_dashboard() dashboard construction."""

    @pytest.fixture
    def mock_citizen(self) -> MagicMock:
        """Create a mock citizen."""
        from agents.town.polynomial import CitizenPhase
        from protocols.nphase.operad import NPhase

        citizen = MagicMock()
        citizen.id = "alice-123"
        citizen.name = "Alice"
        citizen.archetype = "builder"
        citizen._phase = CitizenPhase.WORKING
        citizen.nphase_state.current_phase = NPhase.ACT
        citizen.accursed_surplus = 2.0
        citizen.region = "plaza"
        citizen._infer_mood.return_value = "focused"
        citizen.eigenvectors.warmth = 0.7
        citizen.eigenvectors.curiosity = 0.8
        citizen.eigenvectors.trust = 0.6
        return citizen

    @pytest.fixture
    def mock_env(self, mock_citizen: MagicMock) -> MagicMock:
        """Create a mock environment."""
        env = MagicMock()
        env.name = "testville"
        env.citizens = {"alice-123": mock_citizen}
        env.total_token_spend = 500
        return env

    @pytest.fixture
    def mock_flux(self) -> MagicMock:
        """Create a mock flux."""
        from agents.i.reactive.colony_dashboard import TownPhase

        flux = MagicMock()
        flux.current_phase.name = "MORNING"
        flux.day = 3
        flux.entropy_budget = 0.95
        return flux

    def test_builds_valid_dashboard(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """Should build a ColonyDashboard from environment state."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)

        # Verify it's a ColonyDashboard
        from agents.i.reactive.colony_dashboard import ColonyDashboard

        assert isinstance(dashboard, ColonyDashboard)

    def test_dashboard_json_has_correct_type(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have type='colony_dashboard'."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert json_output["type"] == "colony_dashboard"

    def test_dashboard_json_has_colony_id(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have colony_id from environment name."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert json_output["colony_id"] == "testville"

    def test_dashboard_json_has_phase(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have phase from flux."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert json_output["phase"] == "MORNING"

    def test_dashboard_json_has_day(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have day from flux."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert json_output["day"] == 3

    def test_dashboard_json_has_metrics(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have metrics with total_events, total_tokens, entropy_budget."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert "metrics" in json_output
        assert json_output["metrics"]["total_events"] == 25
        assert json_output["metrics"]["total_tokens"] == 500
        assert json_output["metrics"]["entropy_budget"] == 0.95

    def test_dashboard_json_has_citizens(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have citizens list with citizen data."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert "citizens" in json_output
        assert len(json_output["citizens"]) == 1

        citizen = json_output["citizens"][0]
        assert citizen["citizen_id"] == "alice-123"
        assert citizen["name"] == "Alice"
        assert citizen["archetype"] == "builder"
        assert citizen["phase"] == "WORKING"
        assert citizen["nphase"] == "ACT"

    def test_dashboard_json_has_grid_cols(
        self, mock_env: MagicMock, mock_flux: MagicMock
    ) -> None:
        """JSON output should have grid_cols."""
        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard._to_json()

        assert json_output["grid_cols"] == 5

    def test_empty_environment(self) -> None:
        """Should handle empty environment gracefully."""
        empty_env = MagicMock()
        empty_env.name = "ghost-town"
        empty_env.citizens = {}
        empty_env.total_token_spend = 0

        mock_flux = MagicMock()
        mock_flux.current_phase.name = "NIGHT"
        mock_flux.day = 1
        mock_flux.entropy_budget = 1.0

        dashboard = build_colony_dashboard(empty_env, mock_flux, tick=0)
        json_output = dashboard._to_json()

        assert json_output["colony_id"] == "ghost-town"
        assert json_output["citizens"] == []
        assert json_output["metrics"]["total_events"] == 0

    def test_phase_mapping_afternoon(self) -> None:
        """Should map AFTERNOON phase correctly."""
        env = MagicMock()
        env.name = "test"
        env.citizens = {}
        env.total_token_spend = 0

        flux = MagicMock()
        flux.current_phase.name = "AFTERNOON"
        flux.day = 1
        flux.entropy_budget = 1.0

        dashboard = build_colony_dashboard(env, flux, tick=0)
        json_output = dashboard._to_json()

        assert json_output["phase"] == "AFTERNOON"

    def test_phase_mapping_evening(self) -> None:
        """Should map EVENING phase correctly."""
        env = MagicMock()
        env.name = "test"
        env.citizens = {}
        env.total_token_spend = 0

        flux = MagicMock()
        flux.current_phase.name = "EVENING"
        flux.day = 1
        flux.entropy_budget = 1.0

        dashboard = build_colony_dashboard(env, flux, tick=0)
        json_output = dashboard._to_json()

        assert json_output["phase"] == "EVENING"

    def test_phase_mapping_night(self) -> None:
        """Should map NIGHT phase correctly."""
        env = MagicMock()
        env.name = "test"
        env.citizens = {}
        env.total_token_spend = 0

        flux = MagicMock()
        flux.current_phase.name = "NIGHT"
        flux.day = 1
        flux.entropy_budget = 1.0

        dashboard = build_colony_dashboard(env, flux, tick=0)
        json_output = dashboard._to_json()

        assert json_output["phase"] == "NIGHT"

    def test_unknown_phase_defaults_to_morning(self) -> None:
        """Should default to MORNING for unknown phases."""
        env = MagicMock()
        env.name = "test"
        env.citizens = {}
        env.total_token_spend = 0

        flux = MagicMock()
        flux.current_phase.name = "UNKNOWN_PHASE"
        flux.day = 1
        flux.entropy_budget = 1.0

        dashboard = build_colony_dashboard(env, flux, tick=0)
        json_output = dashboard._to_json()

        assert json_output["phase"] == "MORNING"
