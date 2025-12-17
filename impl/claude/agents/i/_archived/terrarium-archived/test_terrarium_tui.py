"""
Tests for Terrarium TUI - The Glass Box Visualization.

Tests cover:
- State dataclasses
- Renderer output
- Data source fetching (mocked)
- ASCII art helpers
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.i.terrarium_tui import (
    AgentState,
    PheromoneLevel,
    Resolution,
    TerrariumApp,
    TerrariumDataSource,
    TerrariumRenderer,
    TerrariumState,
    Thought,
    TokenBudget,
    _intensity_char,
    _progress_bar,
    _sparkline,
)

# =============================================================================
# Unit Tests - Dataclasses
# =============================================================================


class TestAgentState:
    """Tests for AgentState dataclass."""

    def test_agent_state_defaults(self) -> None:
        """Test default values."""
        agent = AgentState(
            name="b-gent",
            genus="B",
            status="running",
        )

        assert agent.name == "b-gent"
        assert agent.genus == "B"
        assert agent.status == "running"
        assert agent.cpu_percent == 0.0
        assert agent.memory_mb == 0
        assert agent.replicas_ready == 0
        assert agent.replicas_desired == 0
        assert agent.last_activity == ""

    def test_agent_state_full(self) -> None:
        """Test with all fields populated."""
        agent = AgentState(
            name="l-gent-abc123",
            genus="L",
            status="indexing",
            cpu_percent=75.5,
            memory_mb=256,
            replicas_ready=2,
            replicas_desired=2,
            last_activity="2025-01-01T12:00:00",
        )

        assert agent.cpu_percent == 75.5
        assert agent.memory_mb == 256
        assert agent.replicas_ready == 2


class TestPheromoneLevel:
    """Tests for PheromoneLevel dataclass."""

    def test_pheromone_level(self) -> None:
        """Test pheromone level creation."""
        level = PheromoneLevel(
            ptype="WARNING",
            intensity=0.8,
            count=3,
            top_source="F-gent",
        )

        assert level.ptype == "WARNING"
        assert level.intensity == 0.8
        assert level.count == 3
        assert level.top_source == "F-gent"


class TestThought:
    """Tests for Thought dataclass."""

    def test_thought(self) -> None:
        """Test thought creation."""
        now = datetime.now()
        thought = Thought(
            content="Test suite flaking on graph.py",
            source="F-gent",
            timestamp=now,
            confidence=0.9,
            category="warning",
        )

        assert thought.content == "Test suite flaking on graph.py"
        assert thought.source == "F-gent"
        assert thought.timestamp == now
        assert thought.confidence == 0.9
        assert thought.category == "warning"


class TestTokenBudget:
    """Tests for TokenBudget dataclass."""

    def test_token_budget(self) -> None:
        """Test token budget creation."""
        budget = TokenBudget(
            used=847234,
            limit=1000000,
            burn_rate=12.5,
            top_consumer="L-gent",
            history=[10, 11, 12, 13, 14, 15],
        )

        assert budget.used == 847234
        assert budget.limit == 1000000
        assert budget.burn_rate == 12.5
        assert budget.top_consumer == "L-gent"
        assert len(budget.history) == 6


class TestTerrariumState:
    """Tests for TerrariumState dataclass."""

    def test_terrarium_state_defaults(self) -> None:
        """Test default state."""
        state = TerrariumState()

        assert state.health == "unknown"
        assert state.agents == []
        assert state.pheromones == []
        assert state.thoughts == []
        assert state.budget is None
        assert isinstance(state.last_update, datetime)

    def test_terrarium_state_full(self) -> None:
        """Test fully populated state."""
        state = TerrariumState(
            health="healthy",
            agents=[
                AgentState(name="b-gent", genus="B", status="running"),
                AgentState(name="l-gent", genus="L", status="idle"),
            ],
            pheromones=[
                PheromoneLevel(ptype="WARNING", intensity=0.8, count=2),
            ],
        )

        assert state.health == "healthy"
        assert len(state.agents) == 2
        assert len(state.pheromones) == 1


# =============================================================================
# Unit Tests - ASCII Helpers
# =============================================================================


class TestIntensityChar:
    """Tests for _intensity_char helper."""

    def test_intensity_zero(self) -> None:
        """Test intensity 0."""
        assert _intensity_char(0.0) == " "

    def test_intensity_one(self) -> None:
        """Test intensity 1."""
        assert _intensity_char(1.0) == "█"

    def test_intensity_mid(self) -> None:
        """Test intensity 0.5."""
        char = _intensity_char(0.5)
        assert char in ["░", "▒", "▓"]  # Mid-range char

    def test_intensity_out_of_range(self) -> None:
        """Test intensity out of range (clamped)."""
        assert _intensity_char(-0.5) == " "
        assert _intensity_char(1.5) == "█"


class TestProgressBar:
    """Tests for _progress_bar helper."""

    def test_progress_bar_zero(self) -> None:
        """Test 0% progress."""
        bar = _progress_bar(0.0, 10)
        assert bar == "░░░░░░░░░░"

    def test_progress_bar_full(self) -> None:
        """Test 100% progress."""
        bar = _progress_bar(1.0, 10)
        assert bar == "██████████"

    def test_progress_bar_half(self) -> None:
        """Test 50% progress."""
        bar = _progress_bar(0.5, 10)
        assert bar == "█████░░░░░"

    def test_progress_bar_custom_width(self) -> None:
        """Test custom width."""
        bar = _progress_bar(0.5, 20)
        assert len(bar) == 20
        assert bar.count("█") == 10


class TestSparkline:
    """Tests for _sparkline helper."""

    def test_sparkline_empty(self) -> None:
        """Test empty values."""
        line = _sparkline([], 10)
        assert line == "▁" * 10

    def test_sparkline_single_value(self) -> None:
        """Test single value."""
        line = _sparkline([5], 10)
        assert len(line) == 10

    def test_sparkline_increasing(self) -> None:
        """Test increasing values."""
        values = [1, 2, 3, 4, 5, 6, 7, 8]
        line = _sparkline(values, 8)
        assert len(line) == 8
        # First char should be lower than last
        assert line[0] <= line[-1]

    def test_sparkline_width_padding(self) -> None:
        """Test padding to width."""
        values = [1, 2, 3]
        line = _sparkline(values, 10)
        assert len(line) == 10


# =============================================================================
# Unit Tests - TerrariumRenderer
# =============================================================================


class TestTerrariumRenderer:
    """Tests for TerrariumRenderer class."""

    def test_renderer_creation(self) -> None:
        """Test renderer creation."""
        renderer = TerrariumRenderer(width=100)
        assert renderer.width == 100

    def test_render_empty_state(self) -> None:
        """Test rendering empty state."""
        renderer = TerrariumRenderer()
        state = TerrariumState()

        output = renderer.render(state)

        assert isinstance(output, str)
        assert "TERRARIUM" in output

    def test_render_with_agents(self) -> None:
        """Test rendering with agents."""
        renderer = TerrariumRenderer()
        state = TerrariumState(
            health="healthy",
            agents=[
                AgentState(name="b-gent", genus="B", status="running", cpu_percent=80),
                AgentState(name="l-gent", genus="L", status="idle", cpu_percent=20),
            ],
        )

        output = renderer.render(state)

        assert "B" in output
        assert "L" in output

    def test_render_compact_mode(self) -> None:
        """Test compact rendering mode."""
        renderer = TerrariumRenderer()
        state = TerrariumState(health="healthy")

        output = renderer.render(state, Resolution.COMPACT)

        assert isinstance(output, str)
        # Compact should be shorter
        assert len(output.split("\n")) < len(
            renderer.render(state, Resolution.NORMAL).split("\n")
        )


# =============================================================================
# Unit Tests - TerrariumDataSource
# =============================================================================


class TestTerrariumDataSource:
    """Tests for TerrariumDataSource class."""

    def test_data_source_creation(self) -> None:
        """Test data source creation."""
        source = TerrariumDataSource(namespace="test-ns")
        assert source.namespace == "test-ns"

    def test_add_thought(self) -> None:
        """Test adding thoughts to buffer."""
        source = TerrariumDataSource()

        thought = Thought(
            content="Test thought",
            source="B-gent",
            timestamp=datetime.now(),
            confidence=0.8,
            category="observation",
        )

        source.add_thought(thought)

        assert len(source._thought_buffer) == 1
        assert source._thought_buffer[0].content == "Test thought"

    def test_thought_buffer_limit(self) -> None:
        """Test thought buffer doesn't exceed limit."""
        source = TerrariumDataSource()

        # Add more than 50 thoughts
        for i in range(60):
            source.add_thought(
                Thought(
                    content=f"Thought {i}",
                    source="Test",
                    timestamp=datetime.now(),
                    confidence=0.5,
                    category="test",
                )
            )

        # Buffer should be limited to 50
        assert len(source._thought_buffer) == 50
        # Should contain latest thoughts
        assert source._thought_buffer[-1].content == "Thought 59"


class TestTerrariumDataSourceAsync:
    """Async tests for TerrariumDataSource."""

    @pytest.mark.asyncio
    async def test_fetch_state_returns_state(self) -> None:
        """Test fetch_state returns TerrariumState."""
        source = TerrariumDataSource()

        with (
            patch.object(
                source, "_fetch_agents", new_callable=AsyncMock
            ) as mock_agents,
            patch.object(
                source, "_fetch_pheromones", new_callable=AsyncMock
            ) as mock_ph,
            patch.object(
                source, "_fetch_budget", new_callable=AsyncMock
            ) as mock_budget,
        ):
            mock_agents.return_value = []
            mock_ph.return_value = []
            mock_budget.return_value = TokenBudget(
                used=100,
                limit=1000,
                burn_rate=10.0,
                top_consumer="Test",
            )

            state = await source.fetch_state()

            assert isinstance(state, TerrariumState)
            mock_agents.assert_called_once()
            mock_ph.assert_called_once()
            mock_budget.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_state_health_determination(self) -> None:
        """Test health is determined from agent states."""
        source = TerrariumDataSource()

        with (
            patch.object(
                source, "_fetch_agents", new_callable=AsyncMock
            ) as mock_agents,
            patch.object(
                source, "_fetch_pheromones", new_callable=AsyncMock
            ) as mock_ph,
            patch.object(
                source, "_fetch_budget", new_callable=AsyncMock
            ) as mock_budget,
        ):
            mock_ph.return_value = []
            mock_budget.return_value = None

            # No agents = unhealthy
            mock_agents.return_value = []
            state = await source.fetch_state()
            assert state.health == "unhealthy"

            # All running = healthy
            mock_agents.return_value = [
                AgentState(name="b-gent", genus="B", status="running"),
                AgentState(name="l-gent", genus="L", status="running"),
            ]
            state = await source.fetch_state()
            assert state.health == "healthy"

            # Some not running = degraded
            mock_agents.return_value = [
                AgentState(name="b-gent", genus="B", status="running"),
                AgentState(name="l-gent", genus="L", status="starting"),
            ]
            state = await source.fetch_state()
            assert state.health == "degraded"


# =============================================================================
# Unit Tests - TerrariumApp
# =============================================================================


class TestTerrariumApp:
    """Tests for TerrariumApp class."""

    def test_app_creation(self) -> None:
        """Test app creation."""
        app = TerrariumApp()

        assert app.data_source is not None
        assert app.renderer is not None
        assert app.refresh_interval == 2.0
        assert app.resolution == Resolution.NORMAL
        assert app._running is False

    def test_app_custom_config(self) -> None:
        """Test app with custom config."""
        source = TerrariumDataSource(namespace="custom-ns")
        app = TerrariumApp(
            data_source=source,
            refresh_interval=5.0,
            resolution=Resolution.COMPACT,
        )

        assert app.data_source.namespace == "custom-ns"
        assert app.refresh_interval == 5.0
        assert app.resolution == Resolution.COMPACT

    def test_stop(self) -> None:
        """Test stop method."""
        app = TerrariumApp()
        app._running = True

        app.stop()

        assert app._running is False


# =============================================================================
# CLI Handler Tests
# =============================================================================


# TestObserveHandler removed - observe.py archived in UI factoring cleanup
# TODO: Rebuild observe handler with reactive primitives


class TestTetherHandler:
    """Tests for tether CLI handler."""

    def test_parse_args_agent(self) -> None:
        """Test parsing agent name."""
        from protocols.cli.handlers.tether import _parse_args

        options = _parse_args(["b-gent"])

        assert options.get("agent") == "b-gent"

    def test_parse_args_debug(self) -> None:
        """Test parsing --debug."""
        from protocols.cli.handlers.tether import _parse_args

        options = _parse_args(["l-gent", "--debug"])

        assert options.get("agent") == "l-gent"
        assert options.get("debug") is True

    def test_parse_args_port(self) -> None:
        """Test parsing --port."""
        from protocols.cli.handlers.tether import _parse_args

        options = _parse_args(["b-gent", "--port", "9999"])

        assert options.get("agent") == "b-gent"
        assert options.get("port") == 9999

    def test_parse_args_port_invalid(self) -> None:
        """Test --port with invalid value."""
        from protocols.cli.handlers.tether import _parse_args

        options = _parse_args(["b-gent", "--port", "abc"])

        assert "error" in options
