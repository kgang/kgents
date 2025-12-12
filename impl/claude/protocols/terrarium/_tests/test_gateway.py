"""Tests for Terrarium Gateway.

Tests that don't require FastAPI (the FastAPI-specific tests
would need a test client which requires the dependency).
"""

from typing import AsyncIterator

import pytest
from protocols.terrarium.config import TerrariumConfig
from protocols.terrarium.gateway import (
    AgentNotFoundError,
    AgentRegistration,
    Terrarium,
)
from protocols.terrarium.mirror import HolographicBuffer


class TestAgentNotFoundError:
    """AgentNotFoundError exception."""

    def test_error_message(self) -> None:
        """Error includes agent_id in message."""
        err = AgentNotFoundError("test-agent-123")

        assert err.agent_id == "test-agent-123"
        assert "test-agent-123" in str(err)


class TestAgentRegistration:
    """AgentRegistration dataclass."""

    @pytest.mark.asyncio
    async def test_registration_holds_agent_and_mirror(self) -> None:
        """Registration bundles agent with mirror."""
        # Use a mock agent-like object
        from dataclasses import dataclass

        @dataclass
        class MockAgent:
            state: str = "DORMANT"

        agent = MockAgent()
        mirror = HolographicBuffer()

        reg: AgentRegistration[str, str] = AgentRegistration(
            agent=agent,  # type: ignore
            mirror=mirror,
            metadata={"version": "1.0"},
        )

        assert reg.agent is agent  # type: ignore[comparison-overlap]
        assert reg.mirror is mirror
        assert reg.metadata["version"] == "1.0"


class TestTerrariumRegistry:
    """Agent registry functionality (no FastAPI required)."""

    def test_empty_registry(self) -> None:
        """New terrarium has no agents."""
        terrarium = Terrarium()

        assert len(terrarium.registered_agents) == 0

    def test_register_agent_returns_mirror(self) -> None:
        """register_agent returns the HolographicBuffer."""
        terrarium = Terrarium()

        # Mock agent
        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        mirror = terrarium.register_agent("test-agent", agent)  # type: ignore

        assert isinstance(mirror, HolographicBuffer)
        assert "test-agent" in terrarium.registered_agents

    def test_register_duplicate_raises(self) -> None:
        """Cannot register same agent_id twice."""
        terrarium = Terrarium()

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent1 = MockFluxAgent()
        agent2 = MockFluxAgent()

        terrarium.register_agent("duplicate", agent1)  # type: ignore

        with pytest.raises(ValueError, match="already registered"):
            terrarium.register_agent("duplicate", agent2)  # type: ignore

    def test_unregister_agent(self) -> None:
        """unregister_agent removes agent."""
        terrarium = Terrarium()

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        terrarium.register_agent("to-remove", agent)  # type: ignore

        result = terrarium.unregister_agent("to-remove")

        assert result is True
        assert "to-remove" not in terrarium.registered_agents

    def test_unregister_nonexistent(self) -> None:
        """unregister_agent returns False for unknown agent."""
        terrarium = Terrarium()

        result = terrarium.unregister_agent("does-not-exist")

        assert result is False

    def test_get_agent(self) -> None:
        """get_agent retrieves registered agent."""
        terrarium = Terrarium()

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        terrarium.register_agent("retrieval-test", agent)  # type: ignore

        retrieved = terrarium.get_agent("retrieval-test")

        assert retrieved is agent  # type: ignore[comparison-overlap]

    def test_get_agent_not_found(self) -> None:
        """get_agent returns None for unknown agent."""
        terrarium = Terrarium()

        assert terrarium.get_agent("unknown") is None

    def test_get_mirror(self) -> None:
        """get_mirror retrieves agent's HolographicBuffer."""
        terrarium = Terrarium()

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        registered_mirror = terrarium.register_agent("mirror-test", agent)  # type: ignore

        retrieved_mirror = terrarium.get_mirror("mirror-test")

        assert retrieved_mirror is registered_mirror

    def test_register_with_metadata(self) -> None:
        """Metadata is stored with registration."""
        terrarium = Terrarium()

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        terrarium.register_agent(
            "metadata-test",
            agent,  # type: ignore
            metadata={"description": "Test agent", "version": "2.0"},
        )

        # Metadata is stored in the registration
        # (would be visible via REST API)
        assert "metadata-test" in terrarium.registered_agents


class TestTerrariumConfig:
    """Terrarium uses config values."""

    def test_custom_config(self) -> None:
        """Terrarium accepts custom config."""
        config = TerrariumConfig(
            mirror_history_size=50,
            port=9999,
        )
        terrarium = Terrarium(config=config)

        assert terrarium.config.mirror_history_size == 50
        assert terrarium.config.port == 9999

    def test_mirror_uses_config_history_size(self) -> None:
        """Registered mirrors use config history size."""
        config = TerrariumConfig(mirror_history_size=25)
        terrarium = Terrarium(config=config)

        from dataclasses import dataclass

        @dataclass
        class MockFluxAgent:
            state: str = "DORMANT"
            is_running: bool = False

        agent = MockFluxAgent()
        mirror = terrarium.register_agent("history-test", agent)  # type: ignore

        assert mirror.max_history == 25


class TestTerrariumAppCreation:
    """App creation (requires FastAPI import check)."""

    def test_app_property_raises_without_fastapi(self) -> None:
        """Accessing app without FastAPI raises ImportError."""
        terrarium = Terrarium()

        # This test depends on whether FastAPI is installed
        # In CI without FastAPI, this would raise ImportError
        # With FastAPI installed, it would return an app
        try:
            app = terrarium.app
            # FastAPI is installed, app should exist
            assert app is not None
        except ImportError as e:
            # FastAPI not installed, expected
            assert "FastAPI" in str(e)
