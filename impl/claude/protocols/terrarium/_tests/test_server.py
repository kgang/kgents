"""Tests for TerrariumServer and TerrariumServerConfig."""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from protocols.terrarium.server import (
    TerrariumServer,
    TerrariumServerConfig,
    _parse_bool,
)


class TestParseBool:
    """Boolean parsing from environment variables."""

    def test_true_values(self) -> None:
        """Various true string representations."""
        for value in ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]:
            assert _parse_bool(value) is True

    def test_false_values(self) -> None:
        """Various false string representations."""
        for value in ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF", ""]:
            assert _parse_bool(value) is False

    def test_none_with_default(self) -> None:
        """None uses default value."""
        assert _parse_bool(None, default=True) is True
        assert _parse_bool(None, default=False) is False


class TestTerrariumServerConfigDefaults:
    """Default configuration values."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = TerrariumServerConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.metrics_port == 9090
        assert config.mirror_history_size == 100
        assert config.mirror_broadcast_timeout == 0.1
        assert config.auto_discover is True
        assert config.genus_filter == []
        assert config.semaphores_enabled is True
        assert config.purgatory_endpoint is True
        assert config.observe_requires_auth is False
        assert config.perturb_requires_auth is True

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = TerrariumServerConfig(
            host="127.0.0.1",
            port=9000,
            metrics_port=9091,
            semaphores_enabled=False,
            genus_filter=["flux", "grammar"],
        )

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.metrics_port == 9091
        assert config.semaphores_enabled is False
        assert config.genus_filter == ["flux", "grammar"]


class TestTerrariumServerConfigFromEnv:
    """Configuration from environment variables."""

    def test_from_env_defaults(self) -> None:
        """from_env uses defaults when env vars not set."""
        # Clear relevant env vars
        env_vars = [
            "TERRARIUM_HOST",
            "TERRARIUM_PORT",
            "TERRARIUM_METRICS_PORT",
            "TERRARIUM_MIRROR_HISTORY",
            "TERRARIUM_BROADCAST_TIMEOUT",
            "TERRARIUM_AUTO_DISCOVER",
            "TERRARIUM_GENUS_FILTER",
            "TERRARIUM_SEMAPHORES_ENABLED",
            "TERRARIUM_PURGATORY_ENDPOINT",
            "TERRARIUM_OBSERVE_AUTH",
            "TERRARIUM_PERTURB_AUTH",
        ]

        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars:
                os.environ.pop(var, None)

            config = TerrariumServerConfig.from_env()

            assert config.host == "0.0.0.0"
            assert config.port == 8080
            assert config.metrics_port == 9090

    def test_from_env_custom_values(self) -> None:
        """from_env reads custom values from environment."""
        env = {
            "TERRARIUM_HOST": "192.168.1.1",
            "TERRARIUM_PORT": "9000",
            "TERRARIUM_METRICS_PORT": "9091",
            "TERRARIUM_MIRROR_HISTORY": "500",
            "TERRARIUM_BROADCAST_TIMEOUT": "0.5",
            "TERRARIUM_AUTO_DISCOVER": "false",
            "TERRARIUM_GENUS_FILTER": "flux, grammar, echo",
            "TERRARIUM_SEMAPHORES_ENABLED": "false",
            "TERRARIUM_PURGATORY_ENDPOINT": "false",
            "TERRARIUM_OBSERVE_AUTH": "true",
            "TERRARIUM_PERTURB_AUTH": "false",
        }

        with patch.dict(os.environ, env, clear=False):
            config = TerrariumServerConfig.from_env()

            assert config.host == "192.168.1.1"
            assert config.port == 9000
            assert config.metrics_port == 9091
            assert config.mirror_history_size == 500
            assert config.mirror_broadcast_timeout == 0.5
            assert config.auto_discover is False
            assert config.genus_filter == ["flux", "grammar", "echo"]
            assert config.semaphores_enabled is False
            assert config.purgatory_endpoint is False
            assert config.observe_requires_auth is True
            assert config.perturb_requires_auth is False

    def test_from_env_empty_genus_filter(self) -> None:
        """Empty genus filter produces empty list."""
        with patch.dict(os.environ, {"TERRARIUM_GENUS_FILTER": ""}, clear=False):
            config = TerrariumServerConfig.from_env()
            assert config.genus_filter == []


class TestTerrariumServer:
    """TerrariumServer lifecycle tests."""

    def test_server_creation_with_defaults(self) -> None:
        """Server can be created with default config."""
        server = TerrariumServer()

        assert server.config is not None
        assert server.config.port == 8080
        assert server._terrarium is None
        assert server._purgatory is None

    def test_server_creation_with_custom_config(self) -> None:
        """Server accepts custom configuration."""
        config = TerrariumServerConfig(port=9000)
        server = TerrariumServer(config=config)

        assert server.config.port == 9000

    def test_purgatory_property(self) -> None:
        """Purgatory property returns None before start."""
        server = TerrariumServer()
        assert server.purgatory is None

    def test_terrarium_property(self) -> None:
        """Terrarium property returns None before start."""
        server = TerrariumServer()
        assert server.terrarium is None


class TestTerrariumServerPurgatory:
    """Purgatory integration tests."""

    @pytest.mark.asyncio
    async def test_init_purgatory_creates_instance(self) -> None:
        """_init_purgatory creates Purgatory instance."""
        server = TerrariumServer()
        server._terrarium = MagicMock()

        await server._init_purgatory()

        assert server._purgatory is not None
        assert server._purgatory._emit_pheromone is not None

    @pytest.mark.asyncio
    async def test_purgatory_emission_callback(self) -> None:
        """Purgatory emission callback logs events."""
        server = TerrariumServer()
        server._terrarium = MagicMock()

        await server._init_purgatory()

        # Call the emission callback
        assert server._purgatory is not None
        callback = server._purgatory._emit_pheromone
        assert callback is not None

        # Should not raise
        await callback("purgatory.ejected", {"token_id": "test-123"})


class TestTerrariumServerEndpoints:
    """Purgatory REST endpoint tests."""

    def test_add_purgatory_endpoints_skips_without_terrarium(self) -> None:
        """_add_purgatory_endpoints does nothing without terrarium."""
        server = TerrariumServer()
        server._purgatory = MagicMock()

        # Should not raise
        server._add_purgatory_endpoints()

    def test_add_purgatory_endpoints_skips_without_purgatory(self) -> None:
        """_add_purgatory_endpoints does nothing without purgatory."""
        server = TerrariumServer()
        server._terrarium = MagicMock()
        server._terrarium.app = MagicMock()

        # Should not raise
        server._add_purgatory_endpoints()

    def test_add_ready_endpoint(self) -> None:
        """_add_ready_endpoint adds /ready route."""
        server = TerrariumServer()

        # Create mock app with route tracking
        routes: list[str] = []
        mock_app = MagicMock()

        def track_route(path: str) -> Any:
            routes.append(path)
            return lambda f: f

        mock_app.get = track_route

        server._terrarium = MagicMock()
        server._terrarium.app = mock_app

        server._add_ready_endpoint()

        # The decorator was called with /ready path
        assert "/ready" in routes


class TestTerrariumServerIntegration:
    """Integration tests (require FastAPI)."""

    @pytest.mark.asyncio
    async def test_server_initializes_terrarium_and_purgatory(self) -> None:
        """Server components can be initialized together."""
        config = TerrariumServerConfig(semaphores_enabled=True)
        server = TerrariumServer(config=config)

        # Initialize terrarium gateway
        from protocols.terrarium.config import TerrariumConfig
        from protocols.terrarium.gateway import Terrarium

        terrarium_config = TerrariumConfig(
            host=config.host,
            port=config.port,
        )
        server._terrarium = Terrarium(config=terrarium_config)

        # Initialize purgatory
        await server._init_purgatory()

        # Both should now be set
        assert server._terrarium is not None
        assert server._purgatory is not None
        assert server.terrarium is not None
        assert server.purgatory is not None

    @pytest.mark.asyncio
    async def test_purgatory_endpoints_added_when_enabled(self) -> None:
        """Purgatory endpoints are added when purgatory_endpoint=True."""
        config = TerrariumServerConfig(
            semaphores_enabled=True,
            purgatory_endpoint=True,
        )
        server = TerrariumServer(config=config)

        # Initialize components
        from protocols.terrarium.config import TerrariumConfig
        from protocols.terrarium.gateway import Terrarium

        server._terrarium = Terrarium(config=TerrariumConfig())
        await server._init_purgatory()

        # Add endpoints
        server._add_purgatory_endpoints()

        # Verify routes were added (by checking app routes)
        app = server._terrarium.app
        route_paths = [r.path for r in app.routes]

        assert "/api/purgatory/list" in route_paths
        assert "/api/purgatory/{token_id}" in route_paths


class TestServerConfigK8sCompatibility:
    """Ensure config matches K8s AgentServer CRD expectations."""

    def test_config_matches_crd_env_vars(self) -> None:
        """
        Config reads the same env vars that the K8s operator sets.

        From agentserver-crd.yaml, the operator sets:
        - TERRARIUM_PORT
        - TERRARIUM_METRICS_PORT
        - TERRARIUM_AUTO_DISCOVER
        - TERRARIUM_SEMAPHORES_ENABLED
        - TERRARIUM_PURGATORY_ENDPOINT
        - TERRARIUM_OBSERVE_AUTH
        - TERRARIUM_PERTURB_AUTH
        """
        # Simulate what the K8s operator would set
        k8s_env = {
            "TERRARIUM_PORT": "8080",
            "TERRARIUM_METRICS_PORT": "9090",
            "TERRARIUM_AUTO_DISCOVER": "true",
            "TERRARIUM_SEMAPHORES_ENABLED": "true",
            "TERRARIUM_PURGATORY_ENDPOINT": "true",
            "TERRARIUM_OBSERVE_AUTH": "false",
            "TERRARIUM_PERTURB_AUTH": "true",
        }

        with patch.dict(os.environ, k8s_env, clear=False):
            config = TerrariumServerConfig.from_env()

            # All values should be parsed correctly
            assert config.port == 8080
            assert config.metrics_port == 9090
            assert config.auto_discover is True
            assert config.semaphores_enabled is True
            assert config.purgatory_endpoint is True
            assert config.observe_requires_auth is False
            assert config.perturb_requires_auth is True
